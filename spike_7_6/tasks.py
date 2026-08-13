import time
from celery import Celery

REDIS_URL = "redis://127.0.0.1:6379/0"

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

# Fijamos el nombre explícito de la tarea
@celery_app.task(name="calcular_ruta_optima", bind=True, max_retries=3, default_retry_delay=5)
def calcular_ruta_optima(self, envio_id: str, origen: str, destino: str):
    """
    Tarea asíncrona que simula un cálculo pesado de optimización de rutas.
    """
    try:
        time.sleep(3.0)  # Simula cálculo de matriz de distancias
        
        resultado = {
            "envio_id": envio_id,
            "origen": origen,
            "destino": destino,
            "distancia_km": 428.5,
            "tiempo_estimado_hrs": 5.2,
            "ruta_nodos": ["Nodo_A", "Hub_Central", "Nodo_B", "Destino_Final"],
            "estado": "CALCULADO"
        }
        return resultado
    except Exception as exc:
        raise self.retry(exc=exc)
