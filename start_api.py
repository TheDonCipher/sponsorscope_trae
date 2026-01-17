#!/usr/bin/env python3
"""
Startup script for the SponsorScope API with async pipeline.
"""

import uvicorn
import sys
import os

def main():
    """Start the FastAPI application."""
    # Add the current directory to Python path to ensure imports work
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    print("🚀 Starting SponsorScope API with Async Pipeline...")
    print("API will be available at: http://localhost:8000")
    print("Health check: http://localhost:8000/health")
    print("Async health check: http://localhost:8000/api/health/async")
    print("API docs: http://localhost:8000/docs")
    print()
    
    # Run the FastAPI application
    uvicorn.run(
        "services.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()