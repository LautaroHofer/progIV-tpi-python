# ADR 002 - Usamos MongoDB con PyMongo como base de datos principal

## Estado
Aceptado

## Fecha y participantes
19 de noviembre de 2026.
Participaron: Erick Vicentin (en el marco del equipo con Lautaro Hofer y Santiago Nickisch).

## Contexto
El módulo de **Horarios y Turnos** gestiona entidades como horarios de clases, grillas generadas, reservas y listas de espera. En la arquitectura actual (`app/turnos/models/`), los modelos están definidos como clases simples de Python desacopladas del ORM de Django, y la capa de servicios (`app/turnos/services/`) recibe repositorios por inyección de dependencias.

Inicialmente se contempló PostgreSQL con `psycopg2-binary` y la configuración por defecto de Django, pero al avanzar con la implementación de persistencia se evaluó si una base documental se adaptaba mejor al flujo de datos del módulo y al entorno de desarrollo del equipo.

## Opciones consideradas
1. **PostgreSQL con `psycopg2` / Django ORM**:
   - *Ventajas:* Integridad referencial estricta, transacciones SQL multi-tabla maduras y soporte nativo en el ORM de Django.
   - *Desventajas:* Esquema rígido que exige migraciones ante cambios en el modelo de datos, mayor fricción para representar estructuras anidadas (como grillas o listas de espera) y dependencia de binarios nativos (`libpq` / `pg_config`) en versiones recientes de Python como 3.14.
2. **MongoDB con `pymongo` (driver oficial de Python)**:
   - *Ventajas:* Modelo orientado a documentos (BSON/JSON) que encaja de forma natural con los diccionarios de Python, las vistas `JsonResponse` y los modelos desacoplados del ORM; evita migraciones rígidas durante el desarrollo iterativo; se levanta de manera simple y reproducible con Docker (`mongo:7`) y ofrece un pool de conexiones directo mediante `MongoClient`.
   - *Desventajas:* No aprovecha el ORM ni las migraciones automáticas de Django; requiere convertir manualmente `_id` (`ObjectId`) a `str` al serializar respuestas JSON y diseñar explícitamente las actualizaciones atómicas a nivel de documento (por ejemplo, para control de cupos concurrentes).

## Decisión
Se decide utilizar **MongoDB** como base de datos del módulo de Horarios y Turnos, accediendo a través del driver oficial **`pymongo`**:
- Servicio `mongo` (`image: mongo:7`) configurado con volumen persistente en `docker-compose.yml`.
- Dependencia `pymongo` declarada en `requirements.txt`.
- Módulo de conexión centralizado con reutilización de `MongoClient` en `app/infra/db/mongo.py` configurado mediante variables de entorno (`MONGO_URI` y `MONGO_DB_NAME`).
- Persistencia implementada a través de repositorios que respetan la inyección de dependencias de `app/turnos/services/`.

## Consecuencias
- **Qué gana el sistema:** Agilidad para evolucionar el esquema de horarios, reservas y listas de espera; menor boilerplate entre los servicios en Python puro y la base de datos; entorno reproducible con Docker Compose.
- **Qué pierde:** Soporte nativo del ORM de Django (`admin`, `makemigrations`, `migrate`) y validación de esquema impuesta automáticamente por el motor relacional.
- **Qué queda más difícil:** Garantizar consistencia en operaciones que involucren múltiples colecciones simultáneamente (requeriría configurar un Replica Set en MongoDB para transacciones multi-documento o apoyarse en operaciones atómicas por documento).

## Qué nos haría cambiar de decisión
Una necesidad estricta de consultas relacionales complejas con `JOIN`s frecuentes entre múltiples entidades o un requisito explícito de la cátedra de utilizar una base de datos SQL con el ORM de Django.
