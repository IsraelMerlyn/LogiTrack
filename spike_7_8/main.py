import os
import redis
from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from celery.result import AsyncResult
from tasks import celery_app, calcular_ruta_optima

app = FastAPI(
    title="LogiTrack Production Container API — Spike 7.8",
    description="Backend orquestado con FastAPI, Celery, Redis y PostgreSQL"
)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://logitrack_user:logitrack_pass@db:5432/logitrack_db")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Engine para verificación de base de datos
db_engine = create_engine(DATABASE_URL, pool_pre_ping=True)
redis_client = redis.from_url(REDIS_URL)

class RutaRequest(BaseModel):
    envio_id: str
    origen: str
    destino: str

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """Healthcheck robusto que valida conectividad con PostgreSQL y Redis"""
    services_status = {"status": "ok", "db": "healthy", "redis": "healthy"}
    
    # 1. Chequeo de PostgreSQL
    try:
        with db_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        services_status["db"] = f"unhealthy: {str(e)}"
        services_status["status"] = "degraded"

    # 2. Chequeo de Redis
    try:
        redis_client.ping()
    except Exception as e:
        services_status["redis"] = f"unhealthy: {str(e)}"
        services_status["status"] = "degraded"

    if services_status["status"] != "ok":
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=services_status)
        
    return services_status

@app.post("/api/v1/rutas/asincrono", status_code=status.HTTP_202_ACCEPTED)
def calcular_asincrono(payload: RutaRequest):
    task = calcular_ruta_optima.delay(payload.envio_id, payload.origen, payload.destino)
    return {
        "task_id": task.id,
        "status_url": f"/api/v1/rutas/status/{task.id}",
        "message": "Tarea despachada al cluster de workers en Celery"
    }

@app.get("/api/v1/rutas/status/{task_id}")
def obtener_estado(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": task_result.status,
        "resultado": task_result.result if task_result.status == "SUCCESS" else None
    }
