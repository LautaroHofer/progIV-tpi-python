# API - Endpoints del backend Python (Horarios y Turnos)

Base URL: `http://localhost:8000`

## Salud
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health` | Proceso vivo |
| GET | `/ready` | Listo para recibir peticiones |

## Horarios y Grilla
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/horarios/` | Listar clases y horarios disponibles |
| POST | `/api/horarios/generar-grilla` | Generar grilla trimestral de clases |

## Turnos y Reservas
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/turnos/` | Listar turnos reservados |
| POST | `/api/turnos/reservar` | Reservar un turno |
| POST | `/api/turnos/<id>/cancelar` | Cancelar un turno reservado |

## Lista de Espera
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/lista-espera/` | Unirse a la lista de espera de una clase |
| GET | `/api/lista-espera/<clase_id>` | Consultar lista de espera de una clase |
