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
            --primary: #0066ff;
            --secondary: #00d97e;
            --danger: #ff4757;
            --warning: #ffa502;
            --dark: #0f1419;
            --darker: #050609;
            --light: #f8f9fa;
            --border: #1a1f2e;
            --text-primary: #ffffff;
            --text-secondary: #b0b8c1;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', sans-serif;
            background: linear-gradient(135deg, var(--darker) 0%, #0a0e1a 50%, var(--dark) 100%);
            color: var(--text-primary);
            min-height: 100vh;
            background-attachment: fixed;
        }

        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 60px 40px;
        }

        header {
            text-align: center;
            margin-bottom: 80px;
            position: relative;
        }

        header::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 100px;
            height: 3px;
            background: linear-gradient(90deg, transparent, #0066ff, transparent);
        }

        h1 {
            font-size: 3.5em;
            margin-bottom: 15px;
            font-weight: 700;
            letter-spacing: -1px;
            background: linear-gradient(135deg, #0066ff, #00d97e);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: fadeInDown 0.8s ease;
        }

        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .subtitle {
            font-size: 1.3em;
            color: var(--text-secondary);
            margin-bottom: 10px;
            font-weight: 500;
        }

        .subtitle-secondary {
            font-size: 0.95em;
            color: #7a8190;
            margin-top: 8px;
        }

        .module-tabs {
            display: flex;
            gap: 16px;
            margin-bottom: 60px;
            justify-content: center;
            flex-wrap: wrap;
        }

        .tab-btn {
            padding: 14px 32px;
            border: 1.5px solid var(--border);
            background: rgba(15, 20, 25, 0.8);
            color: var(--text-secondary);
            border-radius: 10px;
            cursor: pointer;
            font-size: 1em;
            font-weight: 600;
            transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
            backdrop-filter: blur(10px);
        }

        .tab-btn.active {
            background: linear-gradient(135deg, #0066ff, #0052cc);
            border-color: transparent;
            color: white;
            box-shadow: 0 8px 32px rgba(0, 102, 255, 0.3);
            transform: translateY(-2px);
        }

        .tab-btn:hover:not(.active) {
            border-color: var(--primary);
            color: var(--primary);
            background: rgba(0, 102, 255, 0.05);
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
            gap: 32px;
            margin-bottom: 50px;
            animation: fadeInUp 0.8s ease 0.2s both;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .comparison-card {
            background: linear-gradient(135deg, rgba(15, 20, 25, 0.95), rgba(26, 31, 46, 0.5));
            border: 1.5px solid var(--border);
            border-radius: 16px;
            padding: 40px;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            backdrop-filter: blur(20px);
            position: relative;
            overflow: hidden;
        }

        .comparison-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--primary), transparent);
        }

        .comparison-card:hover {
            border-color: var(--primary);
            box-shadow: 0 20px 60px rgba(0, 102, 255, 0.2);
            transform: translateY(-8px);
        }

        .card-title {
            font-size: 1.6em;
            margin-bottom: 12px;
            color: var(--text-primary);
            font-weight: 700;
        }

        .card-subtitle {
            color: var(--text-secondary);
            margin-bottom: 28px;
            font-size: 0.95em;
            font-weight: 500;
        }

        .metric {
            background: rgba(0, 102, 255, 0.05);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 18px;
            border-left: 3px solid var(--primary);
            transition: all 0.3s;
        }

        .metric:hover {
            background: rgba(0, 102, 255, 0.1);
        }

        .metric-label {
            color: var(--text-secondary);
            font-size: 0.9em;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .metric-value {
            font-size: 2.2em;
            font-weight: 700;
            color: var(--secondary);
            margin-top: 8px;
            letter-spacing: -0.5px;
        }

        .btn {
            padding: 14px 32px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s;
            font-weight: 600;
            text-decoration: none;
            display: inline-block;
        }

        .btn-primary {
            background: linear-gradient(135deg, #0066ff, #0052cc);
            color: white;
            box-shadow: 0 8px 24px rgba(0, 102, 255, 0.3);
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 32px rgba(0, 102, 255, 0.4);
        }

        .status {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 0.85em;
            font-weight: 700;
            margin-top: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .status.good {
            background: rgba(0, 217, 126, 0.15);
            color: #00d97e;
            border: 1px solid rgba(0, 217, 126, 0.3);
        }

        .status.warning {
            background: rgba(255, 165, 2, 0.15);
            color: var(--warning);
            border: 1px solid rgba(255, 165, 2, 0.3);
        }

        .status.bad {
            background: rgba(255, 71, 87, 0.15);
            color: var(--danger);
            border: 1px solid rgba(255, 71, 87, 0.3);
        }

        .info-box {
            background: linear-gradient(135deg, rgba(0, 102, 255, 0.1), rgba(0, 217, 126, 0.05));
            border: 1.5px solid rgba(0, 102, 255, 0.3);
            border-radius: 16px;
            padding: 32px;
            margin-top: 40px;
            backdrop-filter: blur(10px);
        }

        .info-box h3 {
            color: var(--primary);
            margin-bottom: 12px;
            font-size: 1.2em;
            font-weight: 700;
        }

        .info-box p {
            color: var(--text-secondary);
            font-size: 0.95em;
            line-height: 1.6;
        }

        .grid-3 {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 28px;
            animation: fadeInUp 0.8s ease 0.4s both;
        }

        .stat-card {
            background: linear-gradient(135deg, rgba(15, 20, 25, 0.95), rgba(26, 31, 46, 0.5));
            border: 1.5px solid var(--border);
            border-radius: 16px;
            padding: 32px;
            text-align: center;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            backdrop-filter: blur(20px);
            position: relative;
            overflow: hidden;
        }

        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--primary), transparent);
        }

        .stat-card:hover {
            border-color: var(--primary);
            box-shadow: 0 20px 60px rgba(0, 102, 255, 0.15);
            transform: translateY(-8px);
        }

        .stat-number {
            font-size: 3em;
            font-weight: 700;
            color: var(--secondary);
            margin-bottom: 12px;
        }

        .stat-label {
            color: var(--text-primary);
            font-size: 0.95em;
            font-weight: 700;
            letter-spacing: -0.3px;
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
