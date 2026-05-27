"""
Module 1: Async APIs & Concurrency
Main application entry point

This is a simple async API to demonstrate:
- FastAPI basics
- Async request handling
- Response validation with Pydantic
- Error handling
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional
import asyncio
import time
from datetime import datetime
import os

# Create the FastAPI app
app = FastAPI(
    title="Production Systems Lab - Module 1",
    description="Learn async APIs and concurrent request handling",
    version="0.1.0"
)

# Serve frontend
frontend_path = os.path.join(os.path.dirname(__file__), "../../frontend")
if os.path.exists(frontend_path):
    @app.get("/")
    async def serve_frontend():
        """Serve the frontend dashboard"""
        frontend_file = os.path.join(frontend_path, "index.html")
        if os.path.exists(frontend_file):
            return FileResponse(frontend_file)
        return {"message": "Production Systems Lab"}

# ============================================================================
# Data Models (Pydantic)
# ============================================================================

class DataRequest(BaseModel):
    """Request model for data fetching"""
    source_a: bool = Field(True, description="Fetch from source A")
    source_b: bool = Field(True, description="Fetch from source B")
    delay: float = Field(0.1, description="Simulated delay in seconds")


class DataResponse(BaseModel):
    """Response model"""
    data_from_a: Optional[str] = None
    data_from_b: Optional[str] = None
    total_time: float
    fetched_at: datetime


class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    uptime: float


# ============================================================================
# Simulated Data Sources (I/O Operations)
# ============================================================================

async def fetch_from_source_a(delay: float = 1.0) -> str:
    """
    Simulate fetching from an external API or database

    In real production:
    - This would call an external API (aiohttp)
    - Or query a database (asyncpg, sqlalchemy async)
    """
    await asyncio.sleep(delay)
    return f"Data from Source A (fetched at {datetime.now().isoformat()})"


async def fetch_from_source_b(delay: float = 1.0) -> str:
    """
    Simulate fetching from another data source
    """
    await asyncio.sleep(delay)
    return f"Data from Source B (fetched at {datetime.now().isoformat()})"


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """
    Health check endpoint

    Returns status and uptime information.
    Useful for load balancers and monitoring systems.
    """
    return HealthCheck(
        status="healthy",
        timestamp=datetime.now(),
        uptime=time.time()
    )


@app.post("/sync-data", response_model=DataResponse)
async def sync_data(request: DataRequest):
    """
    SEQUENTIAL approach - Fetch data sources one at a time

    This is the slow way. Each fetch waits for the previous one.
    Total time ≈ request.delay * 2 seconds
    """
    start = time.time()

    data_a = None
    data_b = None

    if request.source_a:
        data_a = await fetch_from_source_a(request.delay)

    if request.source_b:
        data_b = await fetch_from_source_b(request.delay)

    elapsed = time.time() - start

    return DataResponse(
        data_from_a=data_a,
        data_from_b=data_b,
        total_time=elapsed,
        fetched_at=datetime.now()
    )


@app.post("/async-data", response_model=DataResponse)
async def async_data(request: DataRequest):
    """
    CONCURRENT approach - Fetch all data sources simultaneously

    This is the fast way using asyncio.gather().
    Total time ≈ request.delay seconds (parallel execution)

    This is why async matters: both sources fetch in parallel,
    but the endpoint only takes as long as the slowest source.
    """
    start = time.time()

    # Prepare tasks
    tasks = []

    if request.source_a:
        tasks.append(fetch_from_source_a(request.delay))

    if request.source_b:
        tasks.append(fetch_from_source_b(request.delay))

    # Run all tasks concurrently
    if tasks:
        results = await asyncio.gather(*tasks)
    else:
        results = []

    elapsed = time.time() - start

    # Unpack results
    data_a = results[0] if request.source_a else None
    data_b = results[1] if request.source_b and len(results) > 1 else None

    return DataResponse(
        data_from_a=data_a,
        data_from_b=data_b,
        total_time=elapsed,
        fetched_at=datetime.now()
    )


@app.get("/api")
async def api_root():
    """
    API root endpoint with documentation
    """
    return {
        "message": "Production Systems Lab - Module 1 API",
        "documentation": "/docs",
        "endpoints": {
            "health": "/health",
            "sync_example": "/sync-data",
            "async_example": "/async-data"
        }
    }


# ============================================================================
# Error Handling
# ============================================================================

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle validation errors gracefully"""
    return {
        "error": "Invalid input",
        "details": str(exc),
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Run code when the API starts

    Useful for:
    - Connecting to databases
    - Loading cache
    - Initializing connections
    """
    print("🚀 API starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Run code when the API shuts down

    Useful for:
    - Closing database connections
    - Saving state
    - Cleanup
    """
    print("🛑 API shutting down...")


# ============================================================================
# Run the Application
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║   Production Systems Lab - Module 1: Async APIs               ║
    ║                                                                ║
    ║   Starting API server...                                       ║
    ║   Visit http://localhost:8000/docs for interactive docs       ║
    ║                                                                ║
    ║   Try these endpoints:                                         ║
    ║   - GET  /health                                              ║
    ║   - POST /sync-data   (sequential, slower)                    ║
    ║   - POST /async-data  (concurrent, faster)                    ║
    ║                                                                ║
    ║   Compare the total_time values to see the difference!        ║
    ╚════════════════════════════════════════════════════════════════╝
    """)

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
