from __future__ import annotations
import os
import json
import asyncio
import uuid
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from shared.schemas.domain import Platform, DataCompleteness
from services.scraper.core.types import ScrapeResult

class Proxy(BaseModel):
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    label: str = "direct"

class ProxyPoolConfig(BaseModel):
    proxies: List[Proxy] = Field(default_factory=list)

    @staticmethod
    def from_env() -> "ProxyPoolConfig":
        raw = os.getenv("PROXY_POOL_JSON")
        if raw:
            try:
                data = json.loads(raw)
                proxies = [Proxy(**p) for p in data.get("proxies", [])]
                if proxies:
                    return ProxyPoolConfig(proxies=proxies)
            except Exception:
                pass
        path = os.getenv("PROXY_POOL_FILE")
        if path and os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    proxies = [Proxy(**p) for p in data.get("proxies", [])]
                    if proxies:
                        return ProxyPoolConfig(proxies=proxies)
            except Exception:
                pass
        return ProxyPoolConfig(proxies=[Proxy()])

class ProxyAssignment(BaseModel):
    proxy: Proxy
    assigned_at: datetime = Field(default_factory=datetime.utcnow)

class ProxyPool:
    def __init__(self, config: ProxyPoolConfig):
        self.config = config
        self._idx = 0

    def assign(self) -> ProxyAssignment:
        if not self.config.proxies:
            p = Proxy()
        else:
            p = self.config.proxies[self._idx % len(self.config.proxies)]
            self._idx = (self._idx + 1) % max(1, len(self.config.proxies))
        return ProxyAssignment(proxy=p)

class BudgetTracker(BaseModel):
    budgets: Dict[str, int] = Field(default_factory=dict)
    counts: Dict[str, Dict[str, int]] = Field(default_factory=dict)

    @staticmethod
    def from_env() -> "BudgetTracker":
        raw = os.getenv("SCRAPE_BUDGETS_JSON")
        budgets: Dict[str, int] = {}
        if raw:
            try:
                data = json.loads(raw)
                budgets = {k.lower(): int(v) for k, v in data.items()}
            except Exception:
                budgets = {}
        return BudgetTracker(budgets=budgets)

    def _key(self, platform: Platform) -> str:
        return platform.value

    def can_consume(self, platform: Platform) -> bool:
        key = self._key(platform)
        limit = self.budgets.get(key)
        if limit is None:
            return True
        today = date.today().isoformat()
        used = self.counts.get(key, {}).get(today, 0)
        return used < limit

    def consume(self, platform: Platform) -> None:
        key = self._key(platform)
        today = date.today().isoformat()
        self.counts.setdefault(key, {})
        self.counts[key][today] = self.counts[key].get(today, 0) + 1

class PaceScheduler:
    def __init__(self):
        base_ms = int(os.getenv("PACING_BASE_MS", "1200"))
        jitter_ms = int(os.getenv("PACING_JITTER_MS", "600"))
        self.base_ms = base_ms
        self.jitter_ms = jitter_ms

    def compute_delay_ms(self, handle: str, attempt: int = 0) -> int:
        seed = (hash(handle) ^ attempt) & 0xFFFFFFFF
        rnd = (1103515245 * seed + 12345) & 0x7FFFFFFF
        jitter = rnd % (self.jitter_ms + 1)
        return self.base_ms + jitter

    async def await_pacing(self, handle: str, attempt: int = 0) -> None:
        ms = self.compute_delay_ms(handle, attempt)
        await asyncio.sleep(ms / 1000.0)

class ScrapeSession(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    handle: str
    platform: Platform
    proxy_label: str
    ip_used: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    attempts: int = 0
    failure_reason: Optional[str] = None

    def to_json(self) -> str:
        return json.dumps(self.dict(), default=str)

class GovernanceProxy:
    def __init__(self):
        self.pool = ProxyPool(ProxyPoolConfig.from_env())
        self.budgets = BudgetTracker.from_env()
        self.pacer = PaceScheduler()

    def start_session(self, handle: str, platform: Platform) -> ScrapeSession:
        assignment = self.pool.assign()
        return ScrapeSession(handle=handle, platform=platform, proxy_label=assignment.proxy.label, ip_used=assignment.proxy.host)

    def can_start(self, platform: Platform) -> bool:
        return self.budgets.can_consume(platform)

    def mark_attempt(self, session: ScrapeSession) -> None:
        session.attempts += 1

    def end_session(self, session: ScrapeSession, success: bool, failure_reason: Optional[str] = None) -> None:
        session.ended_at = datetime.utcnow()
        session.failure_reason = failure_reason
        self._persist_session(session)
        if success:
            self.budgets.consume(session.platform)

    def _persist_session(self, session: ScrapeSession) -> None:
        base_dir = os.path.join(os.getcwd(), "services", "governance", "logs")
        try:
            os.makedirs(base_dir, exist_ok=True)
            path = os.path.join(base_dir, "sessions.jsonl")
            with open(path, "a", encoding="utf-8") as f:
                f.write(session.to_json() + "\n")
        except Exception:
            pass

    def compute_banners(self, result: ScrapeResult, session: ScrapeSession) -> List[str]:
        banners: List[str] = []
        if result.data_completeness != DataCompleteness.FULL:
            banners.append(f"Report generated with partial data: {result.data_completeness.value}")
        if self._is_resistance(result.errors):
            banners.append("Platform resistance detected during scraping")
        if not self.budgets.budgets.get(session.platform.value) is None and not self.can_start(session.platform):
            banners.append("Scan budget reached for platform")
        return banners

    def _is_resistance(self, errors: List[str]) -> bool:
        q = " ".join(errors).lower()
        signals = ["captcha", "rate limit", "challenge", "blocked", "login wall"]
        return any(s in q for s in signals)
