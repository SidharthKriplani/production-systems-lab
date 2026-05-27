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
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional
import asyncio
import time
from datetime import datetime

# Create the FastAPI app
app = FastAPI(
    title="Production Systems Lab - Module 1",
    description="Learn async APIs and concurrent request handling",
    version="0.1.0"
)

# Frontend HTML (embedded directly)
FRONTEND_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Production Systems Lab</title>
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary: #3b82f6;
            --secondary: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
            --dark: #1f2937;
            --darker: #111827;
            --light: #f3f4f6;
            --border: #e5e7eb;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background: linear-gradient(135deg, var(--darker) 0%, #1a202c 100%);
            color: #e5e7eb;
            min-height: 100vh;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 40px 20px;
        }

        header {
            text-align: center;
            margin-bottom: 60px;
            border-bottom: 2px solid var(--primary);
            padding-bottom: 30px;
        }

        h1 {
            font-size: 3em;
            margin-bottom: 10px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .subtitle {
            font-size: 1.2em;
            color: #9ca3af;
            margin-bottom: 20px;
        }

        .module-tabs {
            display: flex;
            gap: 20px;
            margin-bottom: 40px;
            justify-content: center;
            flex-wrap: wrap;
        }

        .tab-btn {
            padding: 12px 24px;
            border: 2px solid var(--border);
            background: transparent;
            color: #e5e7eb;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s;
        }

        .tab-btn.active {
            background: var(--primary);
            border-color: var(--primary);
            color: white;
        }

        .tab-btn:hover {
            border-color: var(--primary);
            color: var(--primary);
        }

        .module-content {
            display: none;
        }

        .module-content.active {
            display: block;
            animation: fadeIn 0.5s;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .comparison-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 40px;
        }

        .comparison-card {
            background: rgba(31, 41, 55, 0.8);
            border: 2px solid var(--border);
            border-radius: 12px;
            padding: 30px;
            transition: all 0.3s;
        }

        .comparison-card:hover {
            border-color: var(--primary);
            box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
        }

        .card-title {
            font-size: 1.5em;
            margin-bottom: 15px;
            color: var(--primary);
        }

        .card-subtitle {
            color: #9ca3af;
            margin-bottom: 20px;
            font-size: 0.9em;
        }

        .metric {
            background: rgba(0, 0, 0, 0.3);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid var(--primary);
        }

        .metric-label {
            color: #9ca3af;
            font-size: 0.9em;
        }

        .metric-value {
            font-size: 1.8em;
            font-weight: bold;
            color: var(--secondary);
            margin-top: 5px;
        }

        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s;
            font-weight: 600;
            text-decoration: none;
            display: inline-block;
        }

        .btn-primary {
            background: var(--primary);
            color: white;
        }

        .btn-primary:hover {
            background: #2563eb;
            transform: translateY(-2px);
        }

        .status {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            margin-top: 10px;
        }

        .status.good {
            background: rgba(16, 185, 129, 0.2);
            color: var(--secondary);
        }

        .status.warning {
            background: rgba(245, 158, 11, 0.2);
            color: var(--warning);
        }

        .status.bad {
            background: rgba(239, 68, 68, 0.2);
            color: var(--danger);
        }

        .info-box {
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid var(--primary);
            border-radius: 8px;
            padding: 20px;
            margin-top: 30px;
        }

        .info-box h3 {
            color: var(--primary);
            margin-bottom: 10px;
        }

        .grid-3 {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }

        .stat-card {
            background: rgba(31, 41, 55, 0.8);
            border: 2px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }

        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
            color: var(--secondary);
            margin-bottom: 10px;
        }

        .stat-label {
            color: #9ca3af;
            font-size: 0.9em;
        }

        @media (max-width: 768px) {
            .comparison-grid {
                grid-template-columns: 1fr;
            }
            h1 {
                font-size: 2em;
            }
        }
    </style>
</head>
<body>
    <div id="root"></div>

    <script type="text/babel">
        function ProductionSystemsLab() {
            const [activeModule, setActiveModule] = React.useState('module1');
            const [module1Data, setModule1Data] = React.useState({
                syncTime: 0.195,
                asyncTime: 0.105,
            });

            const speedup1 = (module1Data.syncTime / module1Data.asyncTime).toFixed(1);

            return (
                <div className="container">
                    <header>
                        <h1>⚡ Production Systems Lab</h1>
                        <p className="subtitle">Master backend systems, scalability, and production engineering</p>
                        <p style={{color: '#6b7280', fontSize: '0.9em'}}>Learn how to build APIs that handle 10,000+ concurrent requests</p>
                    </header>

                    <div className="module-tabs">
                        <button className={`tab-btn ${activeModule === 'module1' ? 'active' : ''}`} onClick={() => setActiveModule('module1')}>
                            Module 1: Async APIs
                        </button>
                        <button className={`tab-btn ${activeModule === 'module2' ? 'active' : ''}`} onClick={() => setActiveModule('module2')}>
                            Module 2: Databases
                        </button>
                        <button className={`tab-btn ${activeModule === 'roadmap' ? 'active' : ''}`} onClick={() => setActiveModule('roadmap')}>
                            Learning Roadmap
                        </button>
                    </div>

                    <div className={`module-content ${activeModule === 'module1' ? 'active' : ''}`}>
                        <div className="comparison-grid">
                            <div className="comparison-card">
                                <h2 className="card-title">❌ Sequential (Slow)</h2>
                                <p className="card-subtitle">Fetch sources one at a time</p>
                                <div className="metric">
                                    <div className="metric-label">Time to fetch 2 sources:</div>
                                    <div className="metric-value">{module1Data.syncTime.toFixed(3)}s</div>
                                </div>
                                <div className="status bad">⚠️ Blocks on I/O operations</div>
                            </div>

                            <div className="comparison-card">
                                <h2 className="card-title">✅ Concurrent (Fast)</h2>
                                <p className="card-subtitle">Fetch sources simultaneously</p>
                                <div className="metric">
                                    <div className="metric-label">Time to fetch 2 sources:</div>
                                    <div className="metric-value">{module1Data.asyncTime.toFixed(3)}s</div>
                                </div>
                                <div className="metric">
                                    <div className="metric-label">Speedup:</div>
                                    <div className="metric-value" style={{color: '#10b981'}}>{speedup1}x faster</div>
                                </div>
                                <div className="status good">✓ Non-blocking with async/await</div>
                            </div>
                        </div>

                        <div className="info-box">
                            <h3>Why This Matters</h3>
                            <p>With 1000 concurrent requests: Sequential takes 200s, Async takes 0.2s = <strong style={{color: '#10b981'}}>1000x faster</strong></p>
                        </div>
                    </div>

                    <div className={`module-content ${activeModule === 'module2' ? 'active' : ''}`}>
                        <div className="comparison-grid">
                            <div className="comparison-card">
                                <h2 className="card-title">❌ N+1 Problem</h2>
                                <p className="card-subtitle">Query in a loop (slow)</p>
                                <div className="metric">
                                    <div className="metric-label">Queries for 5 users:</div>
                                    <div className="metric-value">6 queries</div>
                                </div>
                                <div className="metric">
                                    <div className="metric-label">Response time:</div>
                                    <div className="metric-value">~0.3s</div>
                                </div>
                                <div className="status bad">⚠️ Queries multiply with data</div>
                            </div>

                            <div className="comparison-card">
                                <h2 className="card-title">✅ Join Query</h2>
                                <p className="card-subtitle">Single efficient query (fast)</p>
                                <div className="metric">
                                    <div className="metric-label">Queries for 5 users:</div>
                                    <div className="metric-value">1 query</div>
                                </div>
                                <div className="metric">
                                    <div className="metric-label">Response time:</div>
                                    <div className="metric-value">~0.1s</div>
                                </div>
                                <div className="metric">
                                    <div className="metric-label">Speedup:</div>
                                    <div className="metric-value" style={{color: '#10b981'}}>3x faster</div>
                                </div>
                                <div className="status good">✓ Single JOIN query</div>
                            </div>
                        </div>

                        <div className="info-box">
                            <h3>Database Optimization Impact</h3>
                            <p>Unoptimized queries: 500ms per request. Optimized queries: 10ms per request = <strong style={{color: '#10b981'}}>50x faster</strong></p>
                        </div>
                    </div>

                    <div className={`module-content ${activeModule === 'roadmap' ? 'active' : ''}`}>
                        <div className="grid-3">
                            <div className="stat-card">
                                <div className="stat-number">⚡</div>
                                <div className="stat-label">Module 1: Async APIs</div>
                                <p style={{color: '#d1d5db', marginTop: '10px', fontSize: '0.9em'}}>Handle 1000s of concurrent requests</p>
                            </div>
                            <div className="stat-card">
                                <div className="stat-number">💾</div>
                                <div className="stat-label">Module 2: Databases</div>
                                <p style={{color: '#d1d5db', marginTop: '10px', fontSize: '0.9em'}}>Query optimization & performance</p>
                            </div>
                            <div className="stat-card">
                                <div className="stat-number">🔍</div>
                                <div className="stat-label">Module 3: Observability</div>
                                <p style={{color: '#d1d5db', marginTop: '10px', fontSize: '0.9em'}}>Monitor what's happening (coming)</p>
                            </div>
                        </div>

                        <div className="info-box" style={{marginTop: '40px'}}>
                            <h3>Who This Is For</h3>
                            <p>Data engineers and ML practitioners who want to understand production systems and transition to AI engineering.</p>
                        </div>
                    </div>
                </div>
            );
        }

        ReactDOM.createRoot(document.getElementById('root')).render(<ProductionSystemsLab />);
    </script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the frontend dashboard"""
    return FRONTEND_HTML

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
