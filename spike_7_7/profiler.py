import cProfile
import pstats
import io
import math

def calcular_matriz_distancias_cpu_bound(n_nodos=500):
    """Simulación de algoritmo CPU-Bound sin optimizar"""
    matriz = []
    for i in range(n_nodos):
        fila = []
        for j in range(n_nodos):
            # Cómputo trigonométrico pesado para simular distancia Haversine
            val = math.sin(i) * math.cos(j) + math.sqrt(i * j + 1)
            fila.append(val)
        matriz.append(fila)
    return matriz

def auditar_codigo():
    print("🔬 Ejecutando Profiling de CPU con cProfile...")
    pr = cProfile.Profile()
    pr.enable()

    # Ejecución del fragmento analizado
    resultado = calcular_matriz_distancias_cpu_bound(400)

    pr.disable()
    
    # Formatear reporte de profiling
    s = io.StringIO()
    sortby = pstats.SortKey.CUMULATIVE
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats(10) # Mostrar las 10 funciones más costosas

    print("\n" + "=" * 65)
    print("REPORTE DE PROFILING DE CPU (Top 10 Funciones por Tiempo Acumulado)")
    print("=" * 65)
    print(s.getvalue())

if __name__ == "__main__":
    auditar_codigo()
