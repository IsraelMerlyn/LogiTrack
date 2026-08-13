import time
from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
from celery.result import AsyncResult
from tasks import celery_app, calcular_ruta_optima

app = FastAPI(
    title="LogiTrack Async API — Spike 7.6",
    description="Procesamiento en Segundo Plano con Celery y Redis"
)

class RutaRequest(BaseModel):
    envio_id: str
    origen: str
    destino: str

# 1. Endpoint Síncrono (Bloqueante - Mala Práctica para Tareas Pesadas)
@app.post("/api/v1/rutas/sincrono", status_code=status.HTTP_200_OK)
def calcular_sincrono(payload: RutaRequest):
    t0 = time.perf_counter()
    time.sleep(3.0)  # Bloquea el hilo principal de FastAPI
    t1 = time.perf_counter()
    return {
        "metodo": "SINCRONO_BLOQUEANTE",
        "envio_id": payload.envio_id,
        "tiempo_procesamiento_ms": round((t1 - t0) * 1000, 2),
        "estado": "COMPLETADO"
    }

# 2. Endpoint Asíncrono (No Bloqueante - Buenas Prácticas)
@app.post("/api/v1/rutas/asincrono", status_code=status.HTTP_202_ACCEPTED)
def calcular_asincrono(payload: RutaRequest):
    t0 = time.perf_counter()
    
    # Despachar la tarea al Broker de Celery (Inmediato)
    task = calcular_ruta_optima.delay(payload.envio_id, payload.origen, payload.destino)
    
    t1 = time.perf_counter()
    return {
        "metodo": "ASINCRONO_CELERY",
        "task_id": task.id,
        "status_url": f"/api/v1/rutas/status/{task.id}",
        "tiempo_despacho_ms": round((t1 - t0) * 1000, 2),
        "mensaje": "Tarea encolada con éxito para procesamiento en segundo plano."
    }

# 3. Consulta de Estado de la Tarea Asíncrona
@app.get("/api/v1/rutas/status/{task_id}")
def obtener_estado_tarea(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    
    response = {
        "task_id": task_id,
        "status": task_result.status,
        "resultado": None
    }
    
    if task_result.status == "SUCCESS":
        response["resultado"] = task_result.result
    elif task_result.status == "FAILURE":
        response["error"] = str(task_result.result)
        
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8006, log_level="error")
