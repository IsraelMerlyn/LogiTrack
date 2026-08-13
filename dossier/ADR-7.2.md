# ADR 7.2 — Selección de Framework Web e Interfaz de Concurrencia (WSGI vs ASGI) para LogiTrack

**Decisión:** Seleccionar **FastAPI** (sobre la interfaz asíncrona **ASGI** con el servidor de aplicaciones **Uvicorn**) como el framework web principal para el desarrollo del backend de LogiTrack.

**Contexto:** LogiTrack requiere procesar eventos de telemetría de flotas en tiempo real, exponer APIs RESTful estrictamente tipadas y soportar comunicación bidireccional mediante WebSockets y tareas asíncronas en segundo plano, manteniendo baja latencia y generación automática de documentación OpenAPI.

**Alternativas:** 
1. **Flask (WSGI):** Descartado debido a que su modelo de ejecución síncrono bloquea un hilo por petición. Integrar WebSockets o soporte asíncrono requiere librerías de terceros (Eventlet/Gevent/Flask-SocketIO) que aumentan el acoplamiento y la fragilidad del entorno.
2. **Django (WSGI/ASGI Híbrido):** Descartado por su sobrecarga inicial de memoria RAM (+30% respecto a FastAPI) y complejidad de configuración para microservicios/APIs puras donde el motor de plantillas HTML y el panel de administración monolítico son innecesarios.

**Evidencia:** Métricas promedio registradas en el Spike 7.2 sobre 100 peticiones secuenciales HTTP GET `/health`:
* **Flask (WSGI):** Tiempo de arranque = 222.25 ms | Memoria RAM = 30.98 MB | Latencia Media = 2.22 ms | P95 = 2.80 ms.
* **Django (WSGI):** Tiempo de arranque = 412.10 ms | Memoria RAM = 52.40 MB | Latencia Media = 2.85 ms | P95 = 3.65 ms.
* **FastAPI (ASGI / Uvicorn):** Tiempo de arranque = 385.79 ms | Memoria RAM = 42.91 MB | **Latencia Media = 1.16 ms** | **P95 = 1.41 ms** (reducción del 47% en latencia comparado con Flask y 59% respecto a Django).

**Consecuencias:** Se obtiene soporte nativo para `async/await`, concurrencia asíncrona no bloqueante de I/O, validación de esquemas de datos estricta mediante Pydantic y documentación interactiva automática (`/docs` OpenAPI/Swagger). Se asume la necesidad de integrar y configurar manualmente la capa de persistencia (SQLAlchemy ORM + Alembic) y autenticación.

**Límites:** Válido mientras la lógica de enrutamiento y procesamiento sea mayoritariamente I/O-bound (red, base de datos, caché). Operaciones pesadas CPU-bound deberán ser delegadas fuera del hilo principal usando workers asíncronos (Celery + Redis).

**Revisión:** Reevaluar en la Lección 7.8 (Contenerización y Despliegue) al comparar el comportamiento del worker de Uvicorn frente a Gunicorn en contenedores Docker bajo carga con Locust.
