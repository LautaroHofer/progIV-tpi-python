# ADR 002 - Adopción de Cloud Firestore en el backend de Python

## Estado
Aceptado (reemplaza la configuración inicial con PostgreSQL)

## Fecha y participantes
17 de noviembre de 2026.
Participaron: Lautaro Hofer, Erick Vicentin, Santiago Nickisch.

## Contexto
Inicialmente el servicio de Python tenía configurada una conexión a PostgreSQL mediante `psycopg2`. Sin embargo, el equipo migró el backend de Node.js a **Cloud Firestore** para simplificar el despliegue y manejo de datos sin servidores SQL dedicados. Para que ambos servicios operen sobre la misma fuente de datos, es necesario unificar el motor de persistencia en Python.

## Opciones consideradas
1. **Mantener PostgreSQL con `psycopg2` en Python**:
   - *Ventajas:* Permite usar restricciones relacionales de SQL para las reservas y horarios.
   - *Desventajas:* Divide los datos del sistema en dos tecnologías distintas (Firestore en Node y Postgres en Python), dificultando el mantenimiento y las pruebas locales.
2. **Migrar a Cloud Firestore con `firebase-admin`**:
   - *Ventajas:* Ambos servicios (Node y Python) se conectan al mismo proyecto y comparten la misma estructura de ambientes (`(default)`, `turnapp-uat` y `turnapp-prod`) usando el mismo archivo de credenciales o el emulador local.
   - *Desventajas:* Las validaciones de solapamiento de horarios y el control de cupo deben resolverse en la capa de servicios mediante consultas y transacciones de Firestore.

## Decisión
Se reemplaza `psycopg2` por **`firebase-admin`** en `app/infra/db/conexion.py` y se adapta `app/config/env.py` para usar las mismas variables de entorno y bases por ambiente que el servicio de Node.js.

## Consecuencias
- **Qué gana el sistema:** Consistencia entre los dos repositorios, menor configuración local y acceso directo a las colecciones compartidas.
- **Qué pierde:** Restricciones nativas de SQL sobre intervalos de tiempo.
- **Qué queda más difícil:** El control de concurrencia en las reservas deberá implementarse explícitamente con transacciones de Firestore.

## Qué nos haría cambiar de decisión
Si las transacciones de Firestore presentaran limitaciones de rendimiento para el volumen de reservas concurrentes exigido en las pruebas.
