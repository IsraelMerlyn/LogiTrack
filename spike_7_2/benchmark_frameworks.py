import subprocess
import time
import sys
import os
import requests
import psutil
import statistics

PYTHON_BIN = sys.executable
NUM_REQUESTS = 100

def wait_for_port(url, timeout=5.0):
    start = time.perf_counter()
    while time.perf_counter() - start < timeout:
        try:
            r = requests.get(url, timeout=0.5)
            if r.status_code == 200:
                return (time.perf_counter() - start) * 1000
        except Exception:
            time.sleep(0.01)
    raise TimeoutError(f"El servidor en {url} no arrancó a tiempo.")

def measure_framework(name, cmd, port):
    print(f" Iniciando servidor {name}...")
    
    t0_start = time.perf_counter()
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    url = f"http://127.0.0.1:{port}/health"

    try:
        startup_time_ms = wait_for_port(url)
        
        # Medir memoria RSS del proceso en reposo
        p_info = psutil.Process(proc.pid)
        # Incluir procesos hijos si Uvicorn o Django abren subprocessos
        mem_bytes = p_info.memory_info().rss
        for child in p_info.children(recursive=True):
            mem_bytes += child.memory_info().rss
        mem_mb = mem_bytes / (1024 * 1024)

        # Warm-up (10 peticiones no contabilizadas)
        for _ in range(10):
            requests.get(url)

        # Medición de Latencia (100 peticiones GET)
        latencies = []
        for _ in range(NUM_REQUESTS):
            t0 = time.perf_counter()
            r = requests.get(url)
            t1 = time.perf_counter()
            if r.status_code == 200:
                latencies.append((t1 - t0) * 1000)

        latencies.sort()
        avg_lat = statistics.mean(latencies)
        p95_lat = latencies[int(len(latencies) * 0.95)]

        return {
            "name": name,
            "startup_ms": startup_time_ms,
            "mem_mb": mem_mb,
            "avg_lat": avg_lat,
            "p95_lat": p95_lat
        }

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
        time.sleep(0.5)

if __name__ == "__main__":
    print(" Módulo 7 — Spike 7.2: Benchmark de Frameworks Web (WSGI vs ASGI)\n")

    targets = [
        ("Flask (WSGI)", [PYTHON_BIN, "spike_7_2/app_flask.py"], 8000),
        ("Django (WSGI)", [PYTHON_BIN, "spike_7_2/app_django.py", "runserver", "127.0.0.1:8001", "--noreload"], 8001),
        ("FastAPI (ASGI)", [PYTHON_BIN, "spike_7_2/app_fastapi.py"], 8002)
    ]

    results = []
    for name, cmd, port in targets:
        try:
            res = measure_framework(name, cmd, port)
            results.append(res)
        except Exception as e:
            print(f"❌ Error en {name}: {e}")

    print("\n" + "=" * 65)
    print(f"{'Framework':<18} | {'Arranque (ms)':<13} | {'RAM (MB)':<10} | {'Lat. Media':<10} | {'Lat. P95'}")
    print("=" * 65)
    for r in results:
        print(f"{r['name']:<18} | {r['startup_ms']:>13.2f} | {r['mem_mb']:>10.2f} | {r['avg_lat']:>8.2f} ms | {r['p95_lat']:>6.2f} ms")
    print("=" * 65 + "\n")
