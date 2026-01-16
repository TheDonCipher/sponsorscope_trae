from fastapi import APIRouter, HTTPException, Depends
from services.api.models.report import ReportResponse
from services.governance.core.killswitch import KillSwitch
# from services.orchestrator import scan_orchestrator # TODO: Implement Orchestrator

router = APIRouter()

@router.get("/report/{handle}", response_model=ReportResponse)
async def get_report(handle: str):
    """
    Get or trigger a report for a specific handle.
    """
    # 0. Kill Switch Check (Read)
    if not KillSwitch.is_read_enabled():
        raise HTTPException(status_code=503, detail=KillSwitch.get_maintenance_message())

    # 1. Check Cache (Firestore)
    # cached = await firestore.get_report(handle)
    # if cached: return cached
    
    # 2. Kill Switch Check (Write/Scan)
    if not KillSwitch.is_scan_enabled():
        # If cache miss and scans disabled, return 503
        raise HTTPException(status_code=503, detail="New scans are temporarily paused. Please try again later.")
    
    # 3. Trigger Scan (Cloud Tasks)
    # task_id = await scan_orchestrator.trigger_scan(handle)
    
    # 4. Return 202 Accepted (Polling pattern) or wait (MVP)
    # For MVP scaffold, we'll return a mock or 404
    raise HTTPException(status_code=404, detail="Report not found (Scan trigger not implemented yet)")

@router.get("/evidence/{evidence_id}")
async def get_evidence(evidence_id: str):
    """
    Retrieve specific raw evidence (screenshot/json).
    """
    raise HTTPException(status_code=501, detail="Not implemented")
