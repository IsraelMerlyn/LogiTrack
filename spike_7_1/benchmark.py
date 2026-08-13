import time
import requests
import grpc
import sys
import os
import statistics

sys.path.append(os.path.dirname(__file__))
import user_pb2
import user_pb2_grpc

NUM_REQUESTS = 100

def bench_rest():
    latencies = []
    payload_size = 0
    # Descartar calentamiento
    requests.get("http://127.0.0.1:5000/user/1")

    for i in range(1, NUM_REQUESTS + 1):
        t0 = time.perf_counter()
        resp = requests.get(f"http://127.0.0.1:5000/user/{i}")
        t1 = time.perf_counter()
        if resp.status_code == 200:
            latencies.append((t1 - t0) * 1000)
            payload_size = len(resp.content)

    return latencies, payload_size

def bench_graphql():
    latencies = []
    payload_size = 0
    query = {"query": "query { user(id: 1) { id nombre email ultimoLogin } }"}
    requests.post("http://127.0.0.1:5001/graphql", json=query)

    for i in range(1, NUM_REQUESTS + 1):
        q = {"query": f"query {{ user(id: {i}) {{ id nombre email ultimoLogin }} }}"}
        t0 = time.perf_counter()
        resp = requests.post("http://127.0.0.1:5001/graphql", json=q)
        t1 = time.perf_counter()
        if resp.status_code == 200:
            latencies.append((t1 - t0) * 1000)
            payload_size = len(resp.content)

    return latencies, payload_size

def bench_grpc():
    latencies = []
    payload_size = 0
    channel = grpc.insecure_channel("localhost:5002")
    stub = user_pb2_grpc.UserServiceStub(channel)

    # Calentamiento
    stub.GetUser(user_pb2.UserRequest(id=1))

    for i in range(1, NUM_REQUESTS + 1):
        req = user_pb2.UserRequest(id=i)
        t0 = time.perf_counter()
        res = stub.GetUser(req)
        t1 = time.perf_counter()
        latencies.append((t1 - t0) * 1000)
        payload_size = res.ByteSize()

    channel.close()
    return latencies, payload_size

def print_stats(name, latencies, size):
    latencies.sort()
    avg = statistics.mean(latencies)
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[int(len(latencies) * 0.99)]
    print(f"=== {name} ===")
    print(f" • Latencia Media:  {avg:.2f} ms")
    print(f" • Latencia P95:    {p95:.2f} ms")
    print(f" • Latencia P99:    {p99:.2f} ms")
    print(f" • Payload Promedio: {size} bytes\n")

if __name__ == "__main__":
    print(f"📊 Ejecutando Benchmark de 100 peticiones secuenciales por protocolo...\n")
    
    try:
        r_lat, r_size = bench_rest()
        print_stats("REST (Flask JSON)", r_lat, r_size)
    except Exception as e:
        print(f"❌ Error en REST: {e}")

    try:
        g_lat, g_size = bench_graphql()
        print_stats("GraphQL (Strawberry)", g_lat, g_size)
    except Exception as e:
        print(f"❌ Error en GraphQL: {e}")

    try:
        rpc_lat, rpc_size = bench_grpc()
        print_stats("gRPC (Protobuf)", rpc_lat, rpc_size)
    except Exception as e:
        print(f"❌ Error en gRPC: {e}")
