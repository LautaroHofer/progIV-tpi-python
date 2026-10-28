# TP Programación IV - Backend Python

API Python para el sistema de gestión y reserva de turnos.

## Integrantes (Grupo 1 - Comisión 2)
- Lautaro Hoffer
- Erick Vicentin
- Santiago Nickisch

## Requisitos
- Python 3.11+
- Docker y Docker Compose

## Cómo levantar (clon limpio)

1. Copiá las variables de entorno:
   ```bash
   cp .env.example .env
   ```

2. Levantá la base de datos y la API:
   ```bash
   docker compose up
   ```

3. La API queda disponible en `http://localhost:8000`.

## Endpoints principales
Ver documentación detallada en `docs/api.md`.

- `GET /salud`
- `GET /`

## Documentación
- `docs/api.md` — Endpoints
- `docs/modelo.md` — Modelo de dominio
- `docs/adr/` — Decisiones de arquitectura

## Reglas del repositorio
- Repositorio Git privado.
- Commits propios de cada integrante.
- Pull Requests revisados por otro integrante.
- No subir secretos, `.env` real, ni dependencias instaladas.
