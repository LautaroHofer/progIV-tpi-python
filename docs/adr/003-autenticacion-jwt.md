# ADR 003 - Validación local de JWT con secreto compartido (`HS256`) entre Node.js y Python

## Estado
Aceptado

## Fecha y participantes
19 de noviembre de 2026.
Participaron: Erick Vicentin (en el marco del equipo con Lautaro Hofer y Santiago Nickisch).

## Contexto
La arquitectura del trabajo práctico integra dos servicios independientes:
- **API Node.js (`progIV-tpi-node`):** gestiona usuarios (alumnos, profesores, administradores), sucursales, salas, planes y créditos.
- **API Python (`progIV-tpi-python`):** gestiona horarios, grillas, reservas de turnos y lista de espera.

Los usuarios deben poder autenticarse una sola vez y realizar operaciones en la API de Python (como crear o cancelar reservas a su nombre) validando tanto su identidad como sus permisos, sin duplicar cuentas ni contraseñas entre bases de datos.

## Opciones consideradas
1. **Opción A — Validación local con `JWT_SECRET` compartido (`HS256`):**
   - *Ventajas:* Validación 100% *stateless* en memoria mediante `PyJWT`, latencia mínima, sin dependencia de disponibilidad de Node en cada request y alineada con la configuración existente (`jsonwebtoken` y `JWT_SECRET` en Node).
   - *Desventajas:* Requiere compartir el mismo `JWT_SECRET` entre ambos servicios (si Python se compromete, podría firmar tokens) y los tokens siguen siendo válidos hasta su expiración (`exp`).
2. **Opción B — Validación por consulta HTTP a Node (*Token Introspection*):**
   - *Ventajas:* `JWT_SECRET` permanece únicamente en Node y permite revocación inmediata en cada request.
   - *Desventajas:* Agrega latencia de red en cada endpoint protegido y acopla la disponibilidad de Python a la de Node (*Single Point of Failure*).
3. **Opción C — Firma asimétrica con clave privada/pública (`RS256`):**
   - *Ventajas:* Validación local *stateless* sin compartir secreto de firma (Node firma con clave privada, Python solo verifica con clave pública).
   - *Desventajas:* Mayor complejidad operativa para gestionar y distribuir el par de claves PEM en el alcance del TP.

*(El análisis extendido de estas alternativas se encuentra en `docs/autenticacion-jwt.md`).*

## Decisión
Se adopta la **Opción A (validación local de JWT con algoritmo `HS256` y `JWT_SECRET` compartido)**:
- **Emisor único:** la API de Node.js autentica credenciales y firma los JWT con `JWT_SECRET`.
- **Verificador en Python:** la API de Python valida los tokens localmente en `app/turnos/middlewares/auth.py` usando `PyJWT` (`jwt.decode`) y los decoradores `@requiere_auth`, `@requiere_rol` y `@requiere_permiso`.
- **Endurecimiento según RFC 8725 / OWASP:** se fuerza explícitamente `algorithms=["HS256"]` en la decodificación (rechazando `alg: "none"` y evitando *algorithm confusion*) y se valida la expiración (`exp`).
- **Identidad desde el token:** las operaciones a nombre del usuario toman su identificador desde el claim `sub` del JWT verificado, no desde el cuerpo de la petición.

## Consecuencias
- **Qué gana el sistema:** Autenticación única entre microservicios sin duplicar usuarios ni contraseñas, validación rápida y desacoplada de la red, y separación clara de errores `401 Unauthorized` (autenticación) y `403 Forbidden` (autorización).
- **Qué pierde:** Revocación instantánea de tokens antes de su vencimiento (`exp`), mitigada manteniendo tiempos de expiración acotados.
- **Qué queda más difícil:** Rotar `JWT_SECRET` requiere actualizar la variable de entorno de forma coordinada en ambos servicios.

## Qué nos haría cambiar de decisión
Un requerimiento de revocación inmediata en cada petición (que llevaría a *Token Introspection* o lista de revocación compartida) o la incorporación de múltiples servicios externos que justifiquen migrar a firma asimétrica (`RS256`).
