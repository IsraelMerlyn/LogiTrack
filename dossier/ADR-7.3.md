# ADR 7.3 — Estrategia de Enrutamiento RESTful, Validación Pydantic y Contratos HTTP para LogiTrack

**Decisión:** Adoptar un diseño de API RESTful con controladores fuertemente tipados en FastAPI, utilizando esquemas **Pydantic V2** para la validación y serialización de datos en las capas de entrada/salida, y empleando códigos de estado HTTP semánticos explícitos (`201 Created`, `204 No Content`, `422 Unprocessable Entity`).

**Contexto:** La gestión de la flota vehicular y los envíos en LogiTrack exige la captura estricta de formatos (como placas de vehículos, rangos de capacidad de carga y estados operativos) antes de ejecutar cualquier lógica de negocio o consulta a la base de datos, garantizando contratos de interfaz predecibles y auto-documentados.

**Alternativas:** 
1. **Validación Manual con Diccionarios o Marshmallow:** Descartado por requerir código imperativo repetitivo, elevar el riesgo de fuga de datos o excepciones `500 Internal Server Error` no controladas y carecer de integración nativa con la generación de esquemas OpenAPI.
2. **Uso de Respuestas Genéricas `200 OK` con Payload de Error (`{"success": false}`):** Descartado por violar los estándares RESTful, dificultar el monitoreo de métricas mediante herramientas de observabilidad (que dependen de códigos de estado de red) y sobrecargar la lógica de manejo de errores en los clientes (web/móvil).

**Evidencia:** Pruebas de contrato ejecutadas en el Spike 7.3 sobre el recurso `/api/v1/vehiculos`:
* **Rechazo Inmediato:** Peticiones con formatos de placa o capacidades inválidos fueron bloqueadas en la capa de entrada devolviendo `422 Unprocessable Entity` en **< 1.2 ms**, previniendo la contaminación del estado de la aplicación.
* **Semántica Explícita:** La creación de recursos retornó `201 Created` con la cabecera del nuevo recurso; la eliminación devolvió `204 No Content` sin cuerpo.
* **Contrato Vivo:** Exportación automatizada del esquema OpenAPI (`spike_7_3/openapi.json`) con metadatos completos y validaciones de expresión regular.

**Consecuencias:** Desacoplamiento total entre los DTOs (Data Transfer Objects) de entrada/salida y los futuros modelos de persistencia relacional. Generación automática de documentación interactiva en `/docs` (Swagger UI). Se requiere mantener la disciplina de definir esquemas específicos para operaciones de lectura, creación y actualización parcial.

**Límites:** Válido para validaciones de formato y restricciones de campo individuales. Las validaciones de consistencia de dominio complejo que requieran acceso a la base de datos (como verificación de claves duplicadas o transacciones ACID) se manejarán explícitamente en la capa de controladores o servicios.

**Revisión:** Reevaluar en la Lección 7.5 (Seguridad, Autenticación y Autorización) al integrar middlewares de contexto para inyección de credenciales JWT y roles RBAC.
