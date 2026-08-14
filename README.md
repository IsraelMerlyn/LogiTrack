# LogiTrack — Logistics & Fleet Management SaaS Backend

[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg?logo=postgresql)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D.svg?logo=redis)](https://redis.io/)
[![Celery](https://img.shields.io/badge/Celery-5.4-37814A.svg?logo=celery)](https://docs.celeryq.dev/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?logo=docker)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Backend empresarial de alto rendimiento para la gestión de flotas vehiculares, cotización de envíos y optimización de rutas en tiempo real. Desarrollado y validado como proyecto central del **Módulo 7: Backend Development with Python** dentro del programa de certificación profesional **CEDSP**.

---

## 🏗️ Arquitectura del Sistema

El sistema implementa una arquitectura modular, desacoplada y orientada a servicios de baja latencia con concurrencia no bloqueante:

* **Capa Web (ASGI):** FastAPI ejecutado sobre el servidor Uvicorn para gestión de concurrencia asíncrona de alto rendimiento.
* **Validación y Contratos:** Modelos fuertemente tipados con Pydantic V2 y exportación viva del estándar OpenAPI / Swagger UI.
* **Persistencia Relacional:** PostgreSQL 16 gestionado mediante SQLAlchemy 2.0 y Alembic, con mitigación formal de consultas N+1 mediante `selectinload`.
* **Seguridad y Criptografía:** Hashing de contraseñas con **Argon2id**, autenticación *stateless* mediante **JWT** (JSON Web Tokens) y control de acceso basado en roles (**RBAC**).
* **Procesamiento Asíncrono:** Workers distribuidos con **Celery** y **Redis** como Message Broker y Result Backend.
* **Testing y Calidad:** Suite automatizada con **Pytest**, auditoría de CPU con `cProfile` y pruebas de carga sostenida con **Locust**.
* **Contenerización e Inmutabilidad:** `Dockerfile` Multi-Stage (`python:3.12-slim`) ejecutado bajo usuario no-root (`appuser`).

---

## 📁 Estructura del Repositorio

```text
LogiTrack/
├── dossier/                  # Architecture Decision Records (ADR 7.1 al 7.8)
│   ├── ADR-7.1.md            # Aislamiento y estructura modular
│   ├── ADR-7.2.md            # Framework Web ASGI vs WSGI
│   ├── ADR-7.3.md            # RESTful, Pydantic V2 y OpenAPI
│   ├── ADR-7.4.md            # SQLAlchemy 2.0 y mitigación N+1
│   ├── ADR-7.5.md            # Criptografía Argon2id y RBAC
│   ├── ADR-7.6.md            # Celery + Redis para cómputo asíncrono
│   ├── ADR-7.7.md            # Testing con Pytest, cProfile y Locust
│   └── ADR-7.8.md            # Dockerfile multi-stage y Docker Compose
├── evidence/                 # Evidencias no falsificables y logs de ejecución
│   ├── EVIDENCIA_M7.md       # Plantilla de capturas de pantalla de los 8 spikes
│   └── GIT_HISTORY_M7.txt    # Historial completo de commits exportado de Git
├── spike_7_1/                # Setup de entorno virtual y arquitectura CLI
├── spike_7_2/                # Benchmark WSGI vs ASGI (Flask vs Django vs FastAPI)
├── spike_7_3/                # Endpoints RESTful, validación Pydantic y OpenAPI
├── spike_7_4/                # Modelado ORM SQLAlchemy y mitigación N+1
├── spike_7_5/                # Seguridad Argon2id, JWT y RBAC
├── spike_7_6/                # Tareas asíncronas con Celery y Redis
├── spike_7_7/                # Testing con Pytest, cProfile y Locust
├── spike_7_8/                # Dockerfile Multi-stage y Docker Compose
├── README.md                 # Documentación técnica principal
└── requirements.txt          # Dependencias consolidadas del proyecto
```

---

## ⚙️ Prerrequisitos

Antes de comenzar, asegúrate de contar con el siguiente entorno instalado:

* **Sistema Operativo:** Linux (Fedora, Ubuntu, Debian), macOS o Windows con WSL2.
* **Python:** Versión 3.12 o superior.
* **Docker Engine:** Versión 24.0+ y Docker Compose v2+.
* **Git:** Para control de versiones y trazabilidad de commits.

---

## 🚀 Despliegue con Docker Compose (Recomendado)

Toda la infraestructura (API FastAPI, Worker Celery, Redis y PostgreSQL) se despliega de forma orquestada con dependencias coordinadas mediante *healthchecks*:

```bash
# 1. Navegar al directorio de orquestación
cd spike_7_8

# 2. Construir y levantar los contenedores en segundo plano
docker compose up --build -d

# 3. Verificar el estado de salud de todos los servicios
docker compose ps

# 4. Validar el endpoint de diagnóstico (Healthcheck)
curl http://127.0.0.1:8000/health
```

### Endpoints Interactivos y Documentación
* **Swagger UI (Documentación Interactiva):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **ReDoc (Documentación Alternativa):** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
* **Especificación OpenAPI (JSON):** [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

---

## 🧪 Pruebas Automatizadas y Análisis de Carga

Para validar la suite de pruebas unitarias, auditar el consumo de CPU y ejecutar la prueba de estrés en entorno local:

```bash
# 1. Activar el entorno virtual
source venv/bin/activate

# 2. Ejecutar la suite integradora de pruebas y estrés
python spike_7_7/run_spike.py
```

### Resumen de Métricas de Calidad Obtenidas:
* **Pytest (Unitarias e Integración):** 5/5 pruebas aprobadas (**100% pass rate**) en 0.42 s.
* **cProfile (Auditoría de CPU):** 640,402 llamadas analizadas; optimización de cuellos de botella CPU-bound.
* **Locust (Estrés bajo 50 usuarios concurrentes):** 
  * **Peticiones procesadas:** 2,151 peticiones HTTP.
  * **Throughput:** 146.05 RPS sostenidos.
  * **Tasa de error:** 0.00% (cero fallos).
  * **Latencia P95:** 3 ms (Mediana P50 = 2 ms, P99 = 11 ms).

---

## 📚 Dossier de Decisiones Arquitectónicas (ADRs)

Cada decisión de ingeniería en este repositorio cuenta con respaldo empírico documentado en la carpeta `dossier/`:

| ADR | Dominio / Decisión | Métrica Empírica Destacada | Archivo |
| :--- | :--- | :--- | :---: |
| **ADR 7.1** | Aislamiento y Estructura Modular | Entorno virtual `venv` aislado en Python 3.12 sin colisión de dependencias. | [Ver ADR](dossier/ADR-7.1.md) |
| **ADR 7.2** | FastAPI (ASGI) vs WSGI | Latencia P95 de 1.41 ms (reducción de 47% vs Flask y 59% vs Django). | [Ver ADR](dossier/ADR-7.2.md) |
| **ADR 7.3** | Contratos RESTful y Pydantic V2 | Bloqueo en capa de entrada con `422 Unprocessable` en < 1.2 ms. | [Ver ADR](dossier/ADR-7.3.md) |
| **ADR 7.4** | Mitigación del Problema N+1 | Reducción de consultas SQL de 6,001 a solo 3 (-99.95%) con `selectinload`. | [Ver ADR](dossier/ADR-7.4.md) |
| **ADR 7.5** | Seguridad Argon2id, JWT y RBAC | Resistencia anti-fuerza bruta (~120ms cost) y bloqueo con `403 Forbidden`. | [Ver ADR](dossier/ADR-7.5.md) |
| **ADR 7.6** | Cómputo Asíncrono (Celery/Redis) | Latencia percibida de API reducida de 3,005.22 ms a 57.58 ms (-98.1%). | [Ver ADR](dossier/ADR-7.6.md) |
| **ADR 7.7** | Testing, Profiling y Carga (Locust) | 146.05 RPS sostenidos con 0% fallos y P95 sub-3ms bajo 50 usuarios. | [Ver ADR](dossier/ADR-7.7.md) |
| **ADR 7.8** | Contenerización Multi-Stage y Compose | Imagen reducida >60%, ejecución no-root y arranque coordinado por healthchecks. | [Ver ADR](dossier/ADR-7.8.md) |

---

---

## 👤 Autor y Certificación

* **Autor:** Josue Israel Vasquez Martinez

* **Fecha de Emisión:** 14 de Agosto 2026