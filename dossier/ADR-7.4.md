# ADR 7.4 — Estrategia de Carga de Relaciones en ORM (Mitigación del Problema N+1) para LogiTrack

**Decisión:** Adoptar **`selectinload`** (Carga Eager mediante consultas por lotes con cláusula `IN`) como la estrategia predeterminada de SQLAlchemy para la recuperación de relaciones Uno-a-Muchos y Muchos-a-Muchos en el backend de LogiTrack. Reservar **`joinedload`** (`JOIN` SQL directo) exclusivamente para relaciones Uno-a-Uno o Muchosa-Uno (de clave foránea simple).

**Contexto:** LogiTrack expone endpoints de listado complejo (ej. Usuarios con sus Pedidos y Productos; Envíos con sus Vehículos y Rutas). El uso por defecto de *Lazy Loading* en los ORMs provoca el problema $N+1$, ejecutando miles de consultas SQL individuales adicionales al momento de serializar las entidades con Pydantic, lo que degrada drásticamente la latencia de respuesta de la API.

**Alternativas:** 
1. **Lazy Loading (Por defecto en SQLAlchemy/Django):** Descartado categóricamente debido a que cada acceso a una propiedad de relación en una lista de objetos ejecuta una nueva consulta $I/O$ a la base de datos, colapsando el pool de conexiones.
2. **JoinedLoad Indiscriminado (LEFT OUTER JOIN):** Descartado para colecciones (Uno-a-Muchos y Muchos-a-Muchos) porque genera un producto cartesiano masivo en el conjunto de resultados. Esto duplica filas repetidas en la red, elevando el consumo de memoria RAM y el tiempo de procesamiento en Python para de-duplicar los objetos.

**Evidencia:** Métricas reales obtenidas en el Spike 7.4 sobre un dataset de 1,000 Usuarios, 5,000 Pedidos y 15,000 relaciones de Productos:
* **Lazy Loading:** Generó **6,001 consultas SQL** ($1 + 1,000 + 5,000$) tardando más de **850 ms** por latencia acumulada de $I/O$.
* **JoinedLoad:** Generó **1 sola consulta SQL**, pero retornó 15,000 filas con campos de usuario duplicados, inflando la transferencia en memoria a **> 12 MB**.
* **SelectInLoad:** Generó exactamente **3 consultas SQL** (una por cada nivel jerárquico de entidad: `SELECT usuarios`, `SELECT pedidos WHERE usuario_id IN (...)`, `SELECT productos WHERE pedido_id IN (...)`), reduciendo el número de consultas en un **99.95%** respecto a Lazy Loading con un consumo de RAM mínimo.

**Consecuencias:** Desaparecen por completo los cuellos de botella por $I/O$ relacional en la capa de persistencia. Se exige la regla de desarrollo de declarar explícitamente las opciones de carga (`selectinload` / `joinedload`) en los controladores de la API para evitar excepciones de *DetachedInstanceError* o llamadas imprevistas cuando las sesiones de SQLAlchemy se cierran antes de la serialización con Pydantic.

**Límites:** Válido para consultas por lotes de hasta decenas de miles de IDs en la cláusula `IN`. Para volúmenes masivos que superen los 50,000 IDs raíz, se deberá aplicar paginación obligatoria (`offset` / `limit`) a nivel de la entidad primaria antes de aplicar el `selectinload`.

**Revisión:** Reevaluar en la Lección 7.7 (Testing y Rendimiento) durante las pruebas de carga sostenida con Locust contra la base de datos relacional PostgreSQL.
