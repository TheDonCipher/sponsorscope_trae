from fastapi import FastAPI
from services.api.routes import reports

app = FastAPI(title="SponsorScope API", version="1.0.0")

# Mount the reports router at /api/report
app.include_router(reports.router, prefix="/api", tags=["reports"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}
