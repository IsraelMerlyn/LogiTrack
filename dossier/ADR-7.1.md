# ADR 7.1 — Selección de Protocolo de Comunicación y Estilo Arquitectónico para LogiTrack

**Decisión:** Adoptar una arquitectura monolítica modular exponiendo una interfaz principal basada en API RESTful para clientes externos/web, reservando gRPC/Protobuf para servicios de alta frecuencia e ingesta de telemetría interna.

**Contexto:** LogiTrack requiere gestionar flotas y envíos con baja latencia y facilidad de integración. El Spike 7.1 evaluó la consulta de 10,000 registros de usuarios registrados en SQLite local utilizando 100 peticiones secuenciales por protocolo.

**Alternativas:** 
1. GraphQL fue descartado como protocolo global debido a la sobrecarga en la resolución y *parsing* del esquema en Python (+100% de latencia respecto a REST) sin un beneficio directo para entidades de estructura fija.
2. gRPC puro hacia el navegador web fue descartado como API principal por la complejidad de transporte (*gRPC-Web*) y la falta de compatibilidad nativa con clientes HTTP/1.1 estándar sin un proxy intermediario (Envoy).

**Evidencia:** Trazabilidad obtenida en el benchmark sobre el dataset de 10,000 usuarios:
* **REST (Flask JSON):** Latencia Media = 5.20 ms | P95 = 5.80 ms | Payload = ~124 bytes.
* **GraphQL (Strawberry):** Latencia Media = 10.45 ms | P95 = 11.20 ms | Payload = ~112 bytes.
* **gRPC (Protobuf):** Latencia Media = 1.85 ms | P95 = 2.10 ms | Payload = ~42 bytes (reducción del 66% en ancho de banda respecto a REST).

**Consecuencias:** Desarrollo inicial acelerado con contratos REST públicos (OpenAPI/Swagger) y compatibilidad directa con clientes HTTP, manteniendo un consumo de CPU/RAM mínimo en el servidor sin introducir capas de proxy complejas en la fase inicial.

**Límites:** Válido para throughputs de hasta 1,000 req/s por nodo. Si el volumen de transmisión de coordenadas de vehículos en tiempo real supera las 5,000 lecturas/segundo, la ingesta de datos se aislará en un microservicio dedicado sobre gRPC/WebSockets.

**Revisión:** Reevaluar en la Lección 7.8 (Contenerización y Despliegue) durante las pruebas de carga con Locust.
