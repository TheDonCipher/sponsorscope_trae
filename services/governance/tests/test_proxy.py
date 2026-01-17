import os
import json
import asyncio
import pytest
from services.governance.core.proxy import GovernanceProxy, PaceScheduler, BudgetTracker, ProxyPoolConfig, ProxyPool
from shared.schemas.domain import Platform, DataCompleteness
from services.scraper.core.types import ScrapeResult

@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    for k in ["PROXY_POOL_JSON", "SCRAPE_BUDGETS_JSON", "PACING_BASE_MS", "PACING_JITTER_MS"]:
        monkeypatch.delenv(k, raising=False)

def test_proxy_rotation(monkeypatch):
    pool = {
        "proxies": [
            {"host": "1.1.1.1", "port": 8080, "label": "p1"},
            {"host": "2.2.2.2", "port": 8080, "label": "p2"},
        ]
    }
    monkeypatch.setenv("PROXY_POOL_JSON", json.dumps(pool))
    gp = GovernanceProxy()
    s1 = gp.start_session("userA", Platform.INSTAGRAM)
    s2 = gp.start_session("userB", Platform.INSTAGRAM)
    assert s1.proxy_label == "p1"
    assert s2.proxy_label == "p2"
    s3 = gp.start_session("userC", Platform.INSTAGRAM)
    assert s3.proxy_label == "p1"

def test_pacing_determinism(monkeypatch):
    monkeypatch.setenv("PACING_BASE_MS", "1000")
    monkeypatch.setenv("PACING_JITTER_MS", "500")
    pacer = PaceScheduler()
    d1 = pacer.compute_delay_ms("handle_x", 0)
    d2 = pacer.compute_delay_ms("handle_x", 0)
    d3 = pacer.compute_delay_ms("handle_y", 0)
    assert d1 == d2
    assert d1 != d3

@pytest.mark.asyncio
async def test_await_pacing(monkeypatch):
    monkeypatch.setenv("PACING_BASE_MS", "10")
    monkeypatch.setenv("PACING_JITTER_MS", "0")
    pacer = PaceScheduler()
    start = asyncio.get_event_loop().time()
    await pacer.await_pacing("h", 0)
    end = asyncio.get_event_loop().time()
    assert (end - start) >= 0.01

def test_budgets(monkeypatch):
    monkeypatch.setenv("SCRAPE_BUDGETS_JSON", json.dumps({"instagram": 1}))
    gp = GovernanceProxy()
    assert gp.can_start(Platform.INSTAGRAM)
    s = gp.start_session("a", Platform.INSTAGRAM)
    gp.end_session(s, success=True)
    assert not gp.can_start(Platform.INSTAGRAM)

def test_banners_resistance(monkeypatch):
    gp = GovernanceProxy()
    s = gp.start_session("h", Platform.INSTAGRAM)
    result = ScrapeResult(
        profile=None,
        posts=[],
        comments=[],
        data_completeness=DataCompleteness.FAILED,
        errors=["captcha triggered", "rate limit"]
    )
    banners = gp.compute_banners(result, s)
    assert any("Platform resistance" in b for b in banners)
