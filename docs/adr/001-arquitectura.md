# ADR 001 - Arquitectura del backend Python (Horarios y Turnos)

## Estado
Aceptado

## Contexto
El sistema se divide en dos repositorios: Node.js maneja el módulo de "Usuarios y Salones", mientras que este repositorio en Python maneja el módulo de "Horarios y Turnos" (grilla de clases, solapamientos, reservas de turnos y lista de espera).

## Decisión
Usar **Django** (junto con Django REST Framework) manteniendo una separación clara entre la capa de dominio (`app/dominio/`) y la infraestructura (`app/infra/`).

## Alternativas descartadas
- **FastAPI / Flask**: se descartaron ya que para este módulo la cátedra requiere trabajar con Django.
- **Acoplar las reglas de negocio a las vistas de Django**: dificulta correr los tests unitarios de dominio sin levantar la base de datos.
