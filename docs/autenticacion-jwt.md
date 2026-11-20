# Estrategias de Autenticación y Validación JWT entre Microservicios (Node.js + Python)

Documento de análisis técnico para debatir y definir cómo validar la identidad y permisos de los usuarios entre las dos APIs del TP:

- **API Node.js (`progIV-tpi-node`):** fuente de verdad de usuarios (alumnos, profesores, admins), sucursales, salas, planes y créditos. Actúa como **emisor de tokens (Identity Provider)**.
- **API Python (`progIV-tpi-python`):** gestión de turnos, horarios, reservas y lista de espera. Actúa como **servidor de recursos (Resource Server)**.

---

## 1. ¿Por qué cada API NO puede tener su propio `JWT_SECRET` independiente?

Esta es la duda más común cuando se conectan dos backends con JWT. Hay dos motivos fundamentales: uno **criptográfico** y otro **arquitectónico**.

### 1.1. Motivo criptográfico (cómo funciona la firma `HS256`)

Un JWT tiene tres partes separadas por puntos: `header.payload.signature`.

Cuando se usa un algoritmo **simétrico** como **HS256** (HMAC-SHA256), la firma se calcula así:

```text
signature = HMAC_SHA256( Base64URL(header) + "." + Base64URL(payload), JWT_SECRET )
```

Para validar el token, Python recalcula exactamente esa misma operación usando su propio secreto y compara el resultado con la `signature` que vino en el token:

- Si Node firma con `SECRET_NODE` y Python intenta verificar con `SECRET_PYTHON` (distinto), **los hashes jamás coinciden**.
- Resultado: Python rechaza **todos** los tokens con `InvalidSignatureError` (`401 Unauthorized`).
- **Conclusión:** con cifrado simétrico (`HS256`), el emisor y el verificador **deben usar exactamente la misma clave**, o el verificador no puede comprobar localmente que el token sea auténtico.

### 1.2. Motivo arquitectónico (¿y si cada API hiciera su propio login con su propio secreto?)

Si cada API emitiera sus propios tokens con su propio `JWT_SECRET`, aparecerían problemas serios de diseño:

1. **Doble autenticación para el cliente:** el frontend/usuario tendría que loguearse dos veces y administrar dos tokens distintos.
2. **Duplicación de usuarios y contraseñas:** habría que replicar usuarios, hashes de contraseñas y roles tanto en Firestore (Node) como en MongoDB (Python).
3. **Desincronización de seguridad:** si un usuario cambia su contraseña, cambia de rol o es dado de baja en Node, seguiría teniendo acceso válido en Python hasta que se sincronice.
4. **Ruptura de única fuente de verdad (*Single Source of Truth*):** en microservicios, cada dominio tiene un único dueño. La identidad pertenece a Node; Python solo consume esa identidad verificada.

> **¿Existe una forma de que Python NO conozca el secreto con el que firma Node?**  
> Sí, hay dos caminos válidos: **delegar la validación por HTTP a Node (Opción B)** o usar **criptografía asimétrica con clave privada/pública (Opción C, `RS256`)**, donde siguen sin ser "dos secretos independientes", sino un par de claves matemáticamente vinculadas.

---

## 2. Opción A — Validación local con `JWT_SECRET` compartido (`HS256`)

### Cómo funciona

Ambas APIs comparten el mismo `JWT_SECRET` en sus variables de entorno (`.env`). Node firma el JWT en el login (`jsonwebtoken`) y Python lo verifica localmente en cada request protegido (`PyJWT`) sin hacer llamadas de red a Node.

```text
Cliente ──(1. POST /api/auth/login)──────────────────────► API Node (firma JWT con JWT_SECRET)
Cliente ◄───────────────────(2. JWT)────────────────────── API Node

Cliente ──(3. POST /api/turnos/reservar + Bearer JWT)────► API Python
                                                             ├─ Valida firma y exp localmente (PyJWT + JWT_SECRET)
                                                             ├─ Verifica rol / permisos del payload
                                                             └─ Crea reserva en MongoDB con sub del token
```

### Estructura típica del payload del JWT

```json
{
  "sub": "usr_8f3a12",
  "email": "alumno@mail.com",
  "rol": "alumno",
  "permisos": ["reservas:crear", "reservas:cancelar"],
  "iat": 1732046400,
  "exp": 1732050000
}
```

### Implementación en Python

- Instalar `PyJWT` (`pip install PyJWT`).
- Crear un módulo de autenticación en `app/turnos/middlewares/auth.py` con decoradores reutilizables:
  - `@requiere_auth`: extrae el header `Authorization: Bearer <token>`, ejecuta `jwt.decode(token, JWT_SECRET, algorithms=["HS256"])` y adjunta el payload a `request.usuario`. Si falta, expiró o la firma es inválida → `401 Unauthorized`.
  - `@requiere_rol(["alumno", "admin"])` o `@requiere_permiso("reservas:crear")`: verifica la autorización sobre `request.usuario`. Si no tiene permisos → `403 Forbidden`.
- **Regla clave de seguridad:** el `alumno_id` de una reserva debe tomarse de `request.usuario["sub"]` y **no** del body JSON enviado por el cliente (salvo que el rol sea `admin` operando por terceros), para evitar suplantación de identidad.

### Ventajas

- **100% *stateless* y muy rápida:** la validación es una operación criptográfica local en memoria (microsegundos), sin llamadas HTTP extra.
- **Desacoplamiento de disponibilidad:** si Node se reinicia o está lento, los endpoints de Python que solo validan sesión siguen respondiendo sin caída en cascada.
- **Implementación simple:** Node ya tiene `jsonwebtoken` y `JWT_SECRET` configurados en `.env.example`, y en Python son ~30 líneas con `PyJWT`.

### Desventajas y riesgos

- **Secreto compartido:** si el entorno de Python se ve comprometido, un atacante obtendría `JWT_SECRET` y podría **firmar/forjar tokens nuevos** válidos también para Node.
- **Rotación coordinada:** si se rota `JWT_SECRET`, hay que actualizarlo simultáneamente en ambos servicios.
- **Revocación no inmediata:** al ser *stateless*, un token sigue siendo válido hasta que vence `exp` (se mitiga usando tiempos de expiración cortos, p. ej. 15–60 minutos).

### Buenas prácticas obligatorias (RFC 8725 / OWASP)

1. **Forzar el algoritmo en la verificación:** pasar siempre `algorithms=["HS256"]` en `jwt.decode(...)`. Nunca confiar en el campo `alg` del header (evita ataques `alg: "none"` o *algorithm confusion*).
2. **Secreto con alta entropía:** mínimo 256 bits (32 bytes aleatorios), nunca hardcodeado en el código fuente.
3. **No guardar datos sensibles en el payload:** el payload está codificado en Base64URL (legible por cualquiera), no encriptado.
4. **Validar siempre `exp`** (y opcionalmente `iss` / `aud` para restringir emisor y audiencia).

---

## 3. Opción B — Validación consultando a Node (*Token Introspection*)

### Cómo funciona

Python **no conoce `JWT_SECRET`**. Cuando recibe un request con `Authorization: Bearer <token>`, realiza una consulta HTTP interna a un endpoint de Node (por ejemplo, `GET {NODE_API_URL}/api/auth/me` o `POST /api/auth/verify`) reenviando el token. Node valida el token (y opcionalmente consulta el estado actual del usuario en Firestore) y devuelve el usuario autenticado y sus permisos.

```text
Cliente ──(1. POST /api/turnos/reservar + Bearer JWT)──► API Python
                                                           │
                                                           ├──(2. GET /api/auth/me + Bearer JWT)──► API Node
                                                           │                                          ├─ Valida JWT
                                                           │                                          └─ Verifica usuario activo
                                                           │◄──(3. 200 OK { id, rol, permisos })────┘
                                                           │
                                                           └─ Crea reserva en MongoDB
```

### Ventajas

- **Cero secretos compartidos:** `JWT_SECRET` vive únicamente en Node. Python nunca tiene capacidad de firmar tokens.
- **Revocación y cambios en tiempo real:** si un usuario es deshabilitado o se le cambian los permisos en Firestore, el efecto es inmediato en el siguiente request a Python sin esperar a que expire el token.
- **Lógica de autenticación centralizada:** si mañana Node cambia de JWT a otro mecanismo (ej. Firebase Auth ID Tokens), Python casi no cambia.

### Desventajas

- **Latencia adicional en cada request:** toda petición protegida en Python paga un viaje HTTP extra a Node.
- **Acoplamiento fuerte de disponibilidad:** Node se convierte en un punto único de fallo (*Single Point of Failure*) para Python. Si Node se cae, ningún endpoint protegido de Python funciona.
- **Mayor carga en Node:** el tráfico de Python multiplica las peticiones que recibe Node.

---

## 4. Alternativa intermedia de producción: Opción C — Criptografía Asimétrica (`RS256` / `ES256`)

Si se quiere **evitar compartir el secreto** (ventaja de la Opción B) **sin perder la validación local *stateless*** (ventaja de la Opción A), el estándar recomendado por OWASP para arquitecturas con múltiples microservicios es usar firmas **asimétricas** (`RS256` o `ES256`):

- **Node** guarda la **clave privada** (`JWT_PRIVATE_KEY`) → es el **único** servicio que puede firmar tokens.
- **Python** recibe únicamente la **clave pública** (`JWT_PUBLIC_KEY`, o la descarga de un endpoint `/.well-known/jwks.json` de Node) → **solo puede verificar** firmas, nunca emitir tokens nuevos.

En código, tanto en `jsonwebtoken` (Node) como en `PyJWT` (Python), el cambio respecto a la Opción A es mínimo: solo se cambia el algoritmo a `RS256` y las variables de entorno pasan de un secreto compartido a clave privada (Node) + clave pública (Python).

---

## 5. Cuadro comparativo

| Criterio | Opción A: `HS256` (Secreto compartido) | Opción B: Introspection vía HTTP a Node | Opción C: `RS256` (Clave privada / pública) |
| :--- | :--- | :--- | :--- |
| **¿Comparte clave secreta?** | Sí (`JWT_SECRET` en ambos) | No (solo Node) | No (privada en Node, pública en Python) |
| **¿Python puede forjar tokens?** | Sí (si es comprometido) | No | No |
| **Latencia por request** | Mínima (validación local) | Mayor (+1 HTTP a Node por request) | Mínima (validación local) |
| **Dependencia de Node para autenticar** | Ninguna (*stateless*) | Total (si cae Node, cae Python) | Ninguna (*stateless*) |
| **Revocación inmediata** | No (hasta que vence `exp`) | Sí | No (hasta que vence `exp`) |
| **Complejidad de setup en el TP** | Baja | Media | Baja / Media (generar par de claves PEM) |

---

## 6. Recomendación para el TP

- **Para una implementación ágil y alineada con el proyecto actual:** **Opción A (`HS256` con `JWT_SECRET` compartido)** es totalmente válida porque ambos servicios son internos, los desarrolla el mismo equipo y Node ya tiene `JWT_SECRET` configurado. Solo hay que respetar RFC 8725 (`algorithms=["HS256"]`, `exp` corto y secreto fuerte).
- **Si se busca el mejor estándar de seguridad entre microservicios sin penalizar performance:** **Opción C (`RS256`)** resuelve el único punto débil de la Opción A con prácticamente el mismo código.
- **Cuándo elegir Opción B (Introspection):** solo si el requisito prioritario fuera revocación inmediata de sesiones en cada request o si Python de todos modos tuviera que consultar a Node en absolutamente todas las operaciones.

---

## 7. Referencias oficiales

- **RFC 7519 — JSON Web Token (JWT):** https://datatracker.ietf.org/doc/html/rfc7519
- **RFC 8725 — JSON Web Token Best Current Practices:** https://datatracker.ietf.org/doc/html/rfc8725
- **OWASP JSON Web Token Cheat Sheet:** https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html
- **PyJWT (Documentación oficial — Python):** https://pyjwt.readthedocs.io/en/stable/usage.html
- **jsonwebtoken (Documentación oficial — Node.js):** https://github.com/auth0/node-jsonwebtoken
- **JWT.io — Introduction:** https://jwt.io/introduction
