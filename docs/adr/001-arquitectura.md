# ADR 001 - Arquitectura del backend Python

## Estado
Aceptado

## Contexto
El TP Final de Programación IV requiere un backend en Python que se conecte a la misma base de datos que el backend de Node.js, exponiendo sus propios endpoints.

## Decisión
Usar FastAPI por su rapidez de desarrollo, validación automática con Pydantic y documentación automática con Swagger/OpenAPI.

## Alternativas descartadas
- **Flask**: requiere más configuración para validación y serialización.
- **Django**: demasiado pesado para este alcance.
