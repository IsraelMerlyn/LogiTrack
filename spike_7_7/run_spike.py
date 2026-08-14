import subprocess
import time
import sys
import os

PYTHON_BIN = sys.executable

def run_all():
    print("=========================================================")
    print("1. EJECUTANDO SUITE DE PRUEBAS UNITARIAS E INTEGRACIÓN")
    print("=========================================================")
    subprocess.run([PYTHON_BIN, "-m", "pytest", "spike_7_7/test_suite.py", "-v"])

    print("\n=========================================================")
    print("2. EJECUTANDO PROFILING DE RENDIMIENTO DE CPU")
    print("=========================================================")
    subprocess.run([PYTHON_BIN, "spike_7_7/profiler.py"])

    print("\n=========================================================")
    print("3. LEVANTANDO SERVIDOR API PARA PRUEBAS DE CARGA")
    print("=========================================================")
    app_proc = subprocess.Popen([
        PYTHON_BIN, "-m", "uvicorn", "spike_7_7.test_suite:app", "--port", "8007", "--log-level", "error"
    ])
    time.sleep(1.5)

    try:
        print("\n=========================================================")
        print("4. EJECUTANDO PRUEBA DE ESTRÉS CON LOCUST (HEADLESS)")
        print("=========================================================")
        # 50 usuarios concurrentes, aceleración de 10 usuarios/segundo, durante 15 segundos
        locust_cmd = [
            PYTHON_BIN, "-m", "locust",
            "-f", "spike_7_7/locustfile.py",
            "--host", "http://127.0.0.1:8007",
            "--headless",
            "-u", "50",
            "-r", "10",
            "--run-time", "15s"
        ]
        subprocess.run(locust_cmd)

    finally:
        app_proc.terminate()
        app_proc.wait()

if __name__ == "__main__":
    run_all()
