# TP Programación IV - Backend Python (Horarios y Turnos)

API en Python con **Django** encargada del módulo de **Horarios y Turnos** (grilla de clases, validación de solapamientos, reservas de turnos y lista de espera) para el sistema de salones de bienestar y pilates.
*(El módulo de Usuarios y Salones se gestiona en el repositorio de Node.js con Express).*

## Integrantes (Grupo 1 - Comisión 2)
- Lautaro Hofer
- Erick Vicentin
- Santiago Nickisch

## Requisitos
- Python 3.11+
- Django 5+
- Docker y Docker Compose

## Cómo levantar (clon limpio)

1. Copiá las variables de entorno:
   ```bash
   cp .env.example .env
   ```

2. Levantá la base de datos y la API con Docker Compose:
   ```bash
   docker compose up
   ```

3. La API queda disponible en `http://localhost:8000`.

## Endpoints principales (Módulo Horarios y Turnos)
Ver documentación detallada en `docs/api.md`.

### Salud y disponibilidad
- `GET /health`
- `GET /ready`
- `GET /salud`

### Horarios y Grilla
- `GET /api/horarios/`
- `POST /api/horarios/generar-grilla`

### Turnos y Reservas
- `GET /api/turnos/`
- `POST /api/turnos/reservar`
- `POST /api/turnos/<id>/cancelar`

### Lista de Espera
- `POST /api/lista-espera/`
- `GET /api/lista-espera/<clase_id>`

## Documentación
- `docs/api.md` — Endpoints (Horarios y Turnos)
- `docs/modelo.md` — Modelo de dominio
- `docs/mediciones.md` — Informe de medición
- `docs/ataque.md` — Bitácora de ataque y respuestas
- `docs/adr/` — Decisiones de arquitectura
