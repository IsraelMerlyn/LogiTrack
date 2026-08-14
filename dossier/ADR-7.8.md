# ADR 7.8 — Arquitectura de Contenerización, Multi-Stage Builds y Orquestación para LogiTrack

**Decisión:** Adoptar un modelo de empaquetado inmutable mediante **Dockerfiles Multi-Stage** basados en `python:3.12-slim` ejecutando el proceso como usuario no-root (`appuser`), y utilizar **Docker Compose** como motor de orquestación local para gestionar la topología completa de microservicios (FastAPI, Celery, Redis y PostgreSQL) mediante dependencias por *healthchecks*.

**Contexto:** El backend de LogiTrack ha evolucionado de un simple script a un ecosistema distribuido. Depender de instalaciones nativas de Python, Redis y PostgreSQL en cada entorno (Desarrollo, Staging, Producción) genera el síndrome *"funciona en mi máquina"*, incrementa el tiempo de *onboarding* de nuevos desarrolladores y eleva el riesgo de discrepancias de versiones o dependencias del sistema operativo.

**Alternativas:** 
1. **Dockerfile Single-Stage (Tradicional):** Descartado. Dejar compiladores (`gcc`), cabeceras de desarrollo (`libpq-dev`) y cachés de `pip` dentro de la imagen final de producción infla su tamaño (fácilmente superando 1 GB) e incrementa drásticamente la superficie de ataque para vulnerabilidades críticas (CVEs).
2. **Despliegue Tradicional (Systemd / Nginx Host):** Descartado. La gestión manual de servicios y entornos virtuales (`venv`) es frágil, difícil de replicar automáticamente en pipelines CI/CD y complica los procesos de *rollback*.
3. **Minikube / Kubernetes Local:** Descartado para el entorno de desarrollo local por su alto consumo de recursos (CPU/RAM) y excesiva complejidad operativa frente a la simplicidad declarativa de Docker Compose.

**Evidencia:** Validaciones ejecutadas en el Spike 7.8:
* **Optimización de Artefacto:** El build *multi-stage* copió exclusivamente los binarios precompilados de la fase `builder` a un entorno `runner` limpio, reduciendo el tamaño de la imagen final en más del 60%.
* **Seguridad (Principio de Mínimo Privilegio):** La directiva `USER appuser` garantiza que si el contenedor es comprometido, el atacante no tendrá privilegios de `root` para escalar al kernel del host.
* **Resiliencia de Arranque (Race Conditions):** La instrucción `depends_on: condition: service_healthy` en `docker-compose.yml` garantizó que ni la API ni el Worker de Celery arrancaran y fallaran prematuramente antes de que PostgreSQL y Redis estuvieran listos para aceptar conexiones TCP.

**Consecuencias:** Todo el entorno de LogiTrack puede levantarse desde cero en cualquier máquina con un solo comando (`docker compose up`). Se establece el contenedor Docker como el artefacto definitivo a promover entre entornos.

**Límites:** Docker Compose es ideal para orquestación en un solo nodo (single-host). Para producción en alta disponibilidad (escalabilidad horizontal, tolerancia a fallos multi-zona), este manifiesto deberá traducirse a *Helm Charts* para Kubernetes o definiciones de tareas para AWS ECS.
