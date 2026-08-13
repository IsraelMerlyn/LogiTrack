# ADR 7.5 — Arquitectura de Seguridad: Hashing Argon2id, Autenticación JWT y Autorización RBAC para LogiTrack

**Decisión:** Implementar un esquema de almacenamiento seguro de contraseñas mediante **Argon2id** (con parámetros `time_cost=3`, `memory_cost=64MB`), autenticación *stateless* basada en **JSON Web Tokens (JWT)** y autorización mediante inyección de dependencias para Control de Acceso Basado en Roles (**RBAC**) en FastAPI.

**Contexto:** LogiTrack administra permisos para múltiples actores con diferentes niveles de privilegios (Administrador de flota, Operador de rutas y Cliente final). Es crítico prevenir ataques de fuerza bruta en el inicio de sesión, proteger el sistema contra escalada de privilegios y garantizar que el servidor no almacene contraseñas en texto plano ni tokens vulnerables a manipulación.

**Alternativas:** 
1. **Hashing con SHA-256 / MD5:** Descartado categóricamente debido a que la velocidad de cálculo de estos algoritmos permite ataques de fuerza bruta de miles de millones de hashes por segundo utilizando GPUs modernas.
2. **Bcrypt:** Descartado en favor de Argon2id por ser el ganador del *Password Hashing Competition*, ofreciendo mayor resistencia contra ataques de hardware especializado (ASICs/GPUs) gracias a su consumo configurable de memoria RAM.
3. **Autenticación Basada en Sesiones de Servidor (Cookies/SQL):** Descartada debido a que exige mantener estado en memoria o base de datos centralizada por cada usuario conectado, complicando la escalabilidad horizontal y la comunicación asíncrona con WebSockets.

**Evidencia:** Pruebas del Spike 7.5 sobre endpoints protegidos (`/api/v1/flota/admin-only`):
* **Hashing Robusto:** El cómputo de Argon2id impone un costo aproximado de ~120 ms por verificación, limitando los intentos de fuerza bruta a un máximo seguro por núcleo sin degradar la experiencia de login legítimo.
* **Aislamiento RBAC:** Un usuario con rol `CLIENTE` intentando acceder a rutas administrativas recibió un rechazo inmediato con **`403 Forbidden`** en **< 1.5 ms**.
* **Protección de Firma:** Peticiones sin token o con el payload del JWT alterado fueron bloqueadas con **`401 Unauthorized`**.

**Consecuencias:** Inmunidad contra ataques de interceptación o suplantación de payload no firmado. Se requiere establecer una estrategia de rotación de claves secretas (`SECRET_KEY`) y una lista de revocación de tokens (blacklist) mediante Redis para casos de *logout* explícito.

**Límites:** Válido para la autenticación directa contra el backend. Para integraciones empresariales futuras con proveedores de identidad externos, se deberá extender la capa de entrada para soportar el flujo OAuth2 / OpenID Connect.

**Revisión:** Reevaluar en la Lección 7.8 (Contenerización y Despliegue) para asegurar la inyección de variables de entorno de claves secretas desde archivos `.env` no versionados.
