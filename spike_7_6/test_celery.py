import subprocess
import time
import sys
import httpx

PYTHON_BIN = sys.executable

def wait_for_server(base_url, timeout=5.0):
    start = time.perf_counter()
    while time.perf_counter() - start < timeout:
        try:
            r = httpx.get(f"{base_url}/openapi.json", timeout=0.5)
            if r.status_code == 200:
                return True
        except Exception:
            time.sleep(0.1)
    return False

def run_async_tests():
    print("🚀 Iniciando Servidor FastAPI (Puerto 8006)...")
    proc = subprocess.Popen([PYTHON_BIN, "spike_7_6/app_celery.py"])
    
    base_url = "http://127.0.0.1:8006"
    if not wait_for_server(base_url):
        proc.terminate()
        raise RuntimeError("El servidor no logró iniciar a tiempo.")

    client = httpx.Client(base_url=base_url)

    try:
        payload = {
            "envio_id": "ENV-9982",
            "origen": "CDMX_Hub",
            "destino": "Oaxaca_Centro"
        }

        print("\n--- 1. Prueba de Endpoint Síncrono (Bloqueante) ---")
        t0 = time.perf_counter()
        res_sync = client.post("/api/v1/rutas/sincrono", json=payload, timeout=10.0)
        t1 = time.perf_counter()
        lat_sync = (t1 - t0) * 1000
        print(f"Status Code: {res_sync.status_code}")
        print(f"⏱️ Tiempo total percibido por el cliente: {lat_sync:.2f} ms")

        print("\n--- 2. Prueba de Endpoint Asíncrono (Celery Task) ---")
        t0 = time.perf_counter()
        res_async = client.post("/api/v1/rutas/asincrono", json=payload, timeout=10.0)
        t1 = time.perf_counter()
        lat_async = (t1 - t0) * 1000
        data_async = res_async.json()
        task_id = data_async["task_id"]
        
        print(f"Status Code: {res_async.status_code} (202 Accepted)")
        print(f"⚡ Tiempo total de respuesta de API: {lat_async:.2f} ms")
        print(f"Task ID generado: {task_id}")

        print("\n--- 3. Polling de Estado de Tarea en Redis/Celery ---")
        status_url = f"/api/v1/rutas/status/{task_id}"
        
        for intencion in range(1, 6):
            res_status = client.get(status_url)
            estado = res_status.json()["status"]
            print(f" Intento {intencion}: Estado = '{estado}'")
            if estado == "SUCCESS":
                print(f"✅ Resultado recuperado de Redis: {res_status.json()['resultado']}")
                break
            time.sleep(1.0)

        print("\n" + "=" * 60)
        print(f"Métrica de Reducción de Latencia API:")
        print(f" • Síncrono:  {lat_sync:.2f} ms")
        print(f" • Asíncrono: {lat_async:.2f} ms (Mejora del {((lat_sync - lat_async)/lat_sync)*100:.1f}%)")
        print("=" * 60 + "\n")

    finally:
        client.close()
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    run_async_tests()
