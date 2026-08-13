# ADR 7.6 — Arquitectura de Procesamiento Asíncrono en Segundo Plano con Celery y Redis para LogiTrack

**Decisión:** Adoptar **Celery** como procesador distribuido de tareas en segundo plano con **Redis** como Message Broker y Result Backend para la plataforma LogiTrack.

**Contexto:** LogiTrack ejecuta operaciones intensivas en cómputo e I/O (como la optimización de matrices de distancia para cálculo de rutas, generación de reportes masivos y notificaciones). Ejecutar estas tareas de forma síncrona dentro del ciclo request-response de la API HTTP bloquea los hilos del servidor web, degrada la latencia p95 y provoca timeouts en los clientes.

**Alternativas:** 
1. **Ejecución Síncrona Inline:** Descartada por bloquear el event loop de la API durante segundos, colapsando la capacidad del servidor bajo concurrencia básica.
2. **`BackgroundTasks` nativo de FastAPI:** Descartado para tareas críticas por ejecutarse dentro del mismo proceso del servidor web, carecer de persistencia ante reinicios inesperados y no soportar monitoreo distribuido ni colas independientes.
3. **RQ (Redis Queue):** Descartado en favor de Celery debido al ecosistema maduro de Celery para tareas periódicas (Celery Beat), políticas avanzadas de reintento con *backoff* exponencial y mejor integración con sistemas distribuidos.

**Evidencia:** Pruebas comparativas ejecutadas en el Spike 7.6 para el cálculo de una ruta logística:
* **Endpoint Síncrono Bloqueante:** Latencia percibida por el cliente = **3,005.22 ms**.
* **Endpoint Asíncrono (Celery + Redis):** Latencia de respuesta de la API = **57.58 ms** (reducción del **98.1%** en el tiempo de respuesta del servidor web).
* **Persistencia y Estado:** Polling en Redis confirmó la transición de estado de `PENDING` a `SUCCESS` recuperando la matriz de nodos calculada tras los 3 segundos de procesamiento diferido.

**Consecuencias:** La API mantiene una latencia ultrabaja e independiente de la duración real del trabajo pesado. Se asume el costo operacional de gestionar procesos *worker* independientes y la instancia de Redis como infraestructura del sistema.

**Límites:** Válido para operaciones en segundo plano diferidas. No aplica para operaciones síncronas que requieran confirmación inmediata en la base de datos previa a la respuesta al cliente (como la validación de credenciales).

**Revisión:** Reevaluar en la Lección 7.8 (Contenerización y Despliegue) al configurar la orquestación multi-contenedor en `docker-compose.yml` (App + Redis + Celery Worker).
