import os
import time
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "logitrack_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True
)

@celery_app.task(name="calcular_ruta_optima", bind=True, max_retries=3, default_retry_delay=5)
def calcular_ruta_optima(self, envio_id: str, origen: str, destino: str):
    try:
        time.sleep(2.0) # Simulación de cómputo en worker distribuido
        return {
            "envio_id": envio_id,
            "origen": origen,
            "destino": destino,
            "distancia_km": 540.2,
            "tiempo_estimado_hrs": 6.5,
            "estado": "PROCESADO_EN_CONTENEDOR"
        }
    except Exception as exc:
        raise self.retry(exc=exc)
