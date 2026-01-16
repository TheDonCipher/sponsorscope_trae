from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="SponsorScope API", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "SponsorScope API is running"}

@app.get("/health")
async def health():
    return {"status": "ok"}

# TODO: Implement routes for:
# - POST /analyze/{handle} (Trigger scan)
# - GET /reports/{handle} (Get cached report)
# - GET /methodology (Public audit)
