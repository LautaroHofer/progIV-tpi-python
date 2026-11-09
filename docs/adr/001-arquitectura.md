# ADR 001 - Usamos arquitectura en capas con Django App (Views, Routes, Services y Models)

## Estado
Aceptado (reemplaza la propuesta preliminar de arquitectura hexagonal)

## Fecha y participantes
8 de noviembre de 2026.
Participaron: Lautaro Hofer, Erick Vicentin, Santiago Nickisch.

## Contexto
El backend en Python está a cargo del módulo de **Horarios y Turnos** (gestión de grilla de clases recurrentes, detección de solapamientos, reservas con cupo estricto y listas de espera).
Se había comenzado con un esquema de arquitectura hexagonal con puertos y adaptadores. Sin embargo, acoplar dicho patrón a Django forzaba al framework a trabajar contra sus convenciones nativas (MVT/capas), aumentando la complejidad innecesariamente sin aportar beneficios reales al alcance del proyecto.

## Opciones consideradas
1. **Arquitectura Hexagonal (Puertos y Adaptadores en Django)**:
   - *Ventajas:* Desacoplamiento teórico del framework.
   - *Desventajas:* Boilerplate excesivo, interfaces abstractas innecesarias en Python dinámico, repositorios duplicados en memoria y pérdida de las ventajas idiomáticas de Django.
2. **Arquitectura en Capas Tradicional de Django (App Turnos con Views, Routes, Services y Models)**:
   - *Ventajas:* Aprovecha la estructura idiomática de Django, separa responsabilidades claramente (vistas/controladores HTTP, capa de servicios para la lógica pesada de solapamientos y grilla, modelos de datos), simplifica las pruebas unitarias y facilita la colaboración fluida entre los tres integrantes.
   - *Desventajas:* Menor aislamiento respecto al ecosistema de Django.

## Decisión
Se decide adoptar una **Arquitectura en Capas de Django** dentro de la app `app/turnos/`:
- `app/turnos/views/`: controladores HTTP que reciben las solicitudes y devuelven respuestas JSON.
- `app/turnos/routes/`: enrutamiento URL modularizado por entidad (`rutas_horarios.py`, `rutas_turnos.py`, etc.).
- `app/turnos/services/`: lógica de negocio pura (validación de solapamientos, reserva de turnos, generación masiva de grilla, lista de espera).
- `app/turnos/models/`: modelos de datos y esquemas de persistencia.
- `app/turnos/middlewares/`: manejo centralizado de errores y observabilidad.

## Consecuencias
- **Qué gana el sistema:** Mayor claridad conceptual, eliminación de archivos y capas intermedias sin uso, facilidad para implementar la concurrencia y la tarea pesada sin pelear con abstracciones forzadas.
- **Qué pierde:** Flexibilidad para reemplazar Django por otro framework sin tocar las rutas.
- **Qué queda más difícil:** Si se quisiera desacoplar completamente el framework web, se requeriría refactorizar los controladores.

## Qué nos haría cambiar de decisión
Un cambio explícito de la cátedra que requiera migrar a otro framework web (como FastAPI) o que exija expresamente el patrón de puertos y adaptadores.
