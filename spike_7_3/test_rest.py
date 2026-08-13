import subprocess
import time
import sys
import json
import httpx

PYTHON_BIN = sys.executable

def run_tests():
    print(" Iniciando servidor FastAPI para validación de API RESTful...")
    proc = subprocess.Popen(
        [PYTHON_BIN, "spike_7_3/app_rest.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # Esperar a que el puerto 8000 responda
    time.sleep(1.5)
    base_url = "http://127.0.0.1:8000"

    client = httpx.Client(base_url=base_url)

    try:
        print("\n--- 1. Prueba de Creación Exitosa (201 Created) ---")
        payload = {
            "placa": "MXN-1234",
            "modelo": "Volvo FH16",
            "capacidad_kg": 25000.0,
            "estado": "ACTIVO"
        }
        res = client.post("/api/v1/vehiculos", json=payload)
        print(f"Status Code: {res.status_code} (Esperado: 201)")
        print(f"Respuesta: {res.json()}")
        assert res.status_code == 201

        print("\n--- 2. Prueba de Validación Pydantic (422 Unprocessable Entity) ---")
        bad_payload = {
            "placa": "INVALIDA",  # No cumple regex ^[A-Z]{3}-\d{3,4}$
            "modelo": "A",         # min_length=2
            "capacidad_kg": -500   # gt=0
        }
        res_bad = client.post("/api/v1/vehiculos", json=bad_payload)
        print(f"Status Code: {res_bad.status_code} (Esperado: 422)")
        print(f"Errores Pydantic capturados: {json.dumps(res_bad.json()['detail'], indent=2)}")
        assert res_bad.status_code == 422

        print("\n--- 3. Prueba de Regla de Negocio Duplicado (400 Bad Request) ---")
        res_dup = client.post("/api/v1/vehiculos", json=payload)
        print(f"Status Code: {res_dup.status_code} (Esperado: 400)")
        print(f"Detalle: {res_dup.json()}")
        assert res_dup.status_code == 400

        print("\n--- 4. Consulta por Recurso Inexistente (404 Not Found) ---")
        res_404 = client.get("/api/v1/vehiculos/999")
        print(f"Status Code: {res_404.status_code} (Esperado: 404)")
        print(f"Detalle: {res_404.json()}")
        assert res_404.status_code == 404

        print("\n--- 5. Exportación del Contrato OpenAPI (Swagger JSON) ---")
        res_schema = client.get("/openapi.json")
        with open("spike_7_3/openapi.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(res_schema.json(), indent=2))
        print(" Contrato 'spike_7_3/openapi.json' generado y exportado con éxito.")

        print("\n TODAS LAS PRUEBAS DE CONTRATO Y VALIDACIÓN PASARON CON ÉXITO.")

    finally:
        client.close()
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    run_tests()
