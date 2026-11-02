# Modelo de dominio

## Entidades principales
- **Sucursal**: `id`, `nombre`, `direccion`, `creado_en`
- **Sala**: `id`, `sucursal_id`, `nombre`, `capacidad`
- **Profesor**: `id`, `nombre`, `email`
- **Alumno**: `id`, `nombre`, `email`, `creditos`
- **Clase**: `id`, `sala_id`, `profesor_id`, `actividad`, `fecha_inicio`, `fecha_fin`, `cupo`
- **Reserva**: `id`, `alumno_id`, `clase_id`, `estado`, `fecha_reserva`
- **ListaEspera**: `id`, `clase_id`, `alumno_id`, `posicion`

## Invariantes
1. El cupo de una clase nunca excede la capacidad de la sala.
2. Un profesor o sala no pueden tener dos clases solapadas.
3. Un alumno no puede tener dos reservas solapadas.
4. Los créditos se descuentan al reservar y se devuelven de forma idempotente al cancelar en término.
