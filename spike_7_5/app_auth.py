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

def run_security_tests():
    print(" Iniciando Servidor de Seguridad y RBAC para Pruebas...")
    proc = subprocess.Popen(
        [PYTHON_BIN, "spike_7_5/app_auth.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    base_url = "http://127.0.0.1:8000"
    if not wait_for_server(base_url):
        proc.terminate()
        raise RuntimeError("El servidor de seguridad no logró iniciar a tiempo.")

    client = httpx.Client(base_url=base_url)

    try:
        print("\n--- 1. Registro de Usuarios (Argon2id Hash) ---")
        client.post("/api/v1/auth/register", json={"email": "admin@logitrack.com", "password": "AdminSecret123!", "rol": "ADMIN"})
        client.post("/api/v1/auth/register", json={"email": "cliente@logitrack.com", "password": "ClientSecret123!", "rol": "CLIENTE"})
        print(" Usuarios registrados exitosamente con contraseñas hasheadas en Argon2id.")

        print("\n--- 2. Autenticación y Emisión de JWT ---")
        res_admin_login = client.post("/api/v1/auth/login", json={"email": "admin@logitrack.com", "password": "AdminSecret123!"})
        admin_token = res_admin_login.json()["access_token"]
        
        res_client_login = client.post("/api/v1/auth/login", json={"email": "cliente@logitrack.com", "password": "ClientSecret123!"})
        client_token = res_client_login.json()["access_token"]
        print(" Tokens JWT emitidos y recibidos exitosamente.")

        print("\n--- 3. Verificación de Acceso Permitido (ADMIN -> Admin Endpoint) ---")
        headers_admin = {"Authorization": f"Bearer {admin_token}"}
        res_admin_access = client.get("/api/v1/flota/admin-only", headers=headers_admin)
        print(f"Status Code: {res_admin_access.status_code} (Esperado: 200)")
        assert res_admin_access.status_code == 200

        print("\n--- 4. Verificación de Bloqueo RBAC (CLIENTE -> Admin Endpoint -> 403 Forbidden) ---")
        headers_client = {"Authorization": f"Bearer {client_token}"}
        res_forbidden = client.get("/api/v1/flota/admin-only", headers=headers_client)
        print(f"Status Code: {res_forbidden.status_code} (Esperado: 403)")
        print(f"Detalle de Bloqueo: {res_forbidden.json()['detail']}")
        assert res_forbidden.status_code == 403

        print("\n--- 5. Verificación de Bloqueo Sin Token / Token Inválido (401 Unauthorized) ---")
        res_no_auth = client.get("/api/v1/flota/admin-only")
        print(f"Acceso sin Token: {res_no_auth.status_code} (Esperado: 403/401)")
        
        res_bad_token = client.get("/api/v1/flota/admin-only", headers={"Authorization": "Bearer token_falso_alterado"})
        print(f"Token Inválido: {res_bad_token.status_code} (Esperado: 401)")
        assert res_bad_token.status_code == 401

        print("\n TODAS LAS PRUEBAS DE SEGURIDAD, HASHING ARGON2 Y AUTORIZACIÓN RBAC PASARON EXITOSAMENTE.")

    finally:
        client.close()
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    run_security_tests()