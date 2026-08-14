# ADR 7.7 — Estrategia de Testing Automatizado (Pytest), Profiling (cProfile) y Pruebas de Carga Sostenida (Locust) para LogiTrack

**Decisión:** Adoptar **Pytest** (con `pytest-mock` y el `TestClient` de FastAPI) como framework estándar para pruebas unitarias y de integración, **cProfile / pstats** para auditoría y profiling determinístico de CPU en algoritmos pesados, y **Locust** en modo *headless* como herramienta de pruebas de carga y estrés para certificar los acuerdos de nivel de servicio (SLAs) de latencia y concurrencia.

**Contexto:** LogiTrack procesa cotizaciones de envío, cálculo de rutas y telemetría de flotas bajo picos de tráfico en tiempo real. Es indispensable prevenir regresiones lógicas, validar respuestas semánticas ante excepciones HTTP de cliente (`400 Bad Request`) y garantizar que el backend soporte concurrencia sin degradar los percentiles de latencia ($P50$, $P95$, $P99$) ni disparar tasas de error.

**Alternativas:** 
1. **Unittest nativo de Python:** Descartado por requerir clases y métodos redundantes (*boilerplate* excesivo), aserciones imperativas menos expresivas y una integración más rígida con fixtures y herramientas modernas de *mocking*.
2. **Pruebas de Carga Básicas con Apache Benchmark (`ab`) o cURL:** Descartadas por no permitir definir flujos de comportamiento de usuario realistas (pesos aleatorios, intervalos de espera *think-time*, rutas compuestas) ni reportar percentiles de latencia detallados.
3. **Profiling exclusivo en Producción (APMs como New Relic o Datadog):** Descartado como mecanismo primario por no evitar la llegada a producción de cuellos de botella CPU-bound evitables durante el ciclo de desarrollo local / CI.

**Evidencia:** Resultados cuantitativos obtenidos en el Spike 7.7:
* **Suite de Pruebas Automatizadas (Pytest):** 5/5 pruebas aprobadas (**100% pass rate**) en **0.42 s**, cubriendo validaciones de reglas de negocio puras, simulación de APIs externas con `@mocker.patch` y validación de endpoints HTTP (`200 OK` y `400 Bad Request`).
* **Auditoría de CPU (cProfile):** Análisis de 640,402 llamadas en 0.194 s para el cómputo matricial de distancias Haversine, identificando que las llamadas trigonométricas y operaciones `.append` concentran el 85% del tiempo acumulado, justificando su delegación asíncrona a workers de Celery.
* **Prueba de Carga y Concurrencia (Locust Headless):**
  * **Concurrencia simulada:** 50 usuarios simultáneos durante 15 segundos.
  * **Peticiones procesadas:** **2,151 peticiones** HTTP totales.
  * **Tasa de fallos:** **0.00%** ($0$ errores).
  * **Throughput alcanzado:** **146.05 req/s (RPS)** sostenidos.
  * **Percentiles de Latencia:** **Mediana (P50) = 2 ms**, **P90 = 3 ms**, **P95 = 3 ms**, **P99 = 11 ms**, **Máximo absoluto = 26 ms**.

**Consecuencias:** Se establece una barrera de calidad automatizada que previene regresiones en el pipeline de integración continua (CI). La arquitectura ASGI con FastAPI demostró estabilidad extrema manteniendo una latencia sub-3ms en el 95% de las solicitudes bajo 50 usuarios concurrentes.

**Límites:** Las mediciones de Locust se ejecutaron sobre un único proceso de Uvicorn en entorno local. En entornos contenerizados de producción con múltiples réplicas detrás de un balanceador de carga (Nginx / Ingress), el rendimiento escalará linealmente según los *workers* configurados.

**Revisión:** Reevaluar en la Lección 7.8 (Contenerización y Despliegue) al configurar el `Dockerfile` multi-stage y el `docker-compose.yml` para orquestar la API, Redis, Celery y la base de datos relacional.
