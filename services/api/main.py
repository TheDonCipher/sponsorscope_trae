from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from services.api.routes import reports, async_routes, governance
from services.api.job_manager import job_registry
from services.api.background_worker import background_worker
from services.governance.middleware import governance_middleware
from services.governance.core.killswitch import KillSwitch
from services.governance.core.rate_limiter import rate_limiter
from services.governance.core.token_manager import token_manager

app = FastAPI(title="SponsorScope API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add governance middleware directly
@app.middleware("http")
async def add_governance_middleware(request: Request, call_next):
    return await governance_middleware(request, call_next)

# Mount the reports router at /api/report
app.include_router(reports.router, prefix="/api", tags=["reports"])

# Mount the async routes at /api
app.include_router(async_routes.router, prefix="/api", tags=["async"])

# Mount governance routes at /api
app.include_router(governance.router, prefix="/api", tags=["governance"])

@app.on_event("startup")
async def startup_event():
    """Initialize async pipeline components on startup."""
    # Start job registry cleanup task
    await job_registry.start_cleanup_task()
    
    # Start background worker
    await background_worker.start()
    
    print("Async pipeline initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup async pipeline components on shutdown."""
    # Stop background worker
    await background_worker.stop()
    
    # Stop job registry cleanup task
    await job_registry.stop_cleanup_task()
    
    print("Async pipeline shutdown completed")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
