import time
import sys
import httpx

BASE_URL = "http://127.0.0.1:8000"

def test_stack():
    client = httpx.Client(base_url=BASE_URL, timeout=10.0)
    print(" Verificando salud del Stack contenerizado en Docker...")

    # 1. Healthcheck
    try:
        res = client.get("/health")
        print(f"Healthcheck Status: {res.status_code}")
        print(f"Detalle: {res.json()}")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"
    except Exception as e:
        print(f"❌ Error al consultar /health: {e}")
        sys.exit(1)

    # 2. Despachar Tarea Asíncrona
    print("\n--- Despachando Tarea Asíncrona a la API Contenerizada ---")
    payload = {
        "envio_id": "DOCKER-TRK-771",
        "origen": "Planta_Norte_Docker",
        "destino": "CEDIS_Sur_Docker"
    }
    res_task = client.post("/api/v1/rutas/asincrono", json=payload)
    print(f"Status Code: {res_task.status_code} (Esperado: 202)")
    task_id = res_task.json()["task_id"]
    print(f"Task ID generado: {task_id}")

    # 3. Polling de Respuesta de Celery Worker
    print("\n--- Consultando Estado en Redis procesado por Celery Worker ---")
    status_url = f"/api/v1/rutas/status/{task_id}"
    for attempt in range(1, 6):
        time.sleep(1.0)
        res_poll = client.get(status_url)
        st = res_poll.json()["status"]
        print(f" Intento {attempt}: Estado = {st}")
        if st == "SUCCESS":
            print(f" Tarea completada por el contenedor Celery Worker: {res_poll.json()['resultado']}")
            print("\n STACK COMPLETO DE DOCKER COMPOSE OPERATIVO Y VALIDADO.")
            return

    print(" Timeout esperando que Celery procesara la tarea.")
    sys.exit(1)

if __name__ == "__main__":
    test_stack()
