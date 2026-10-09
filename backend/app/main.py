# this is the fastapi layer
from fastapi import FastAPI
from app.core.connections import es, redis_client, get_pg_connection
from app.routes.logs import router as logs_router
from app.services.detection_engine import process_events 
from app.routes.alerts import get_alerts
from app.routes.alerts import router as alerts_router
# we are adding this becasue we want to call the process_events from detection_engine whenever we invoke the main method 
from app.routes.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="CyberPulse",
    description="Real-Time Security Log Analytics with AI-Driven Threat Intelligence",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(logs_router)
app.include_router(alerts_router)
app.include_router(auth_router)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CyberPulse",
    }


@app.get("/health/dependencies")
def dependency_health():
    result = {
        "elasticsearch": "unknown",
        "redis": "unknown",
        "postgresql": "unknown",
    }

    # Elasticsearch
    try:
        if es.ping():
            result["elasticsearch"] = "healthy"
        else:
            result["elasticsearch"] = "unhealthy"
    except Exception as e:
        result["elasticsearch"] = f"error: {str(e)}"

    # Redis
    try:
        if redis_client.ping():
            result["redis"] = "healthy"
        else:
            result["redis"] = "unhealthy"
    except Exception as e:
        result["redis"] = f"error: {str(e)}"

    # PostgreSQL
    try:
        with get_pg_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()

        result["postgresql"] = "healthy"

    except Exception as e:
        result["postgresql"] = f"error: {str(e)}"


@app.post("/detect")
def run_detection():
    process_events()
    return {
        "status": "detection_completed"
    }