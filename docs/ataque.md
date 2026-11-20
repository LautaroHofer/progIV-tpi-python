# Bitácora de ataque y respuestas

## Metodología
Durante la semana de ataque cruzado, el sistema estuvo expuesto para que otros grupos intenten encontrar vulnerabilidades. Todas las acciones se registraron acá.

## Intentos realizados (Atacante)

| # | Fecha | Hipótesis | Petición | Resultado esperado | Resultado obtenido | Veredicto |
|---|-------|-----------|----------|--------------------|--------------------|-----------|
| 1 | - | - | - | - | - | - |

## Hallazgos recibidos (Defensor)
Ninguno registrado por el momento.

## Pruebas de seguridad realizadas por nuestro grupo
- [ ] Validación de JWT (algoritmo HS256 forzado, expiración exp).
- [ ] Decoradores `@requiere_auth`, `@requiere_rol`, `@requiere_permiso`.
- [ ] Rechazo de algoritmo `none` en PyJWT.
- [ ] Rechazo de token expirado.
- [ ] Rechazo de token con secreto incorrecto.

## Notas
No hay secretos en el repositorio ni en el historial. Existe `.env.example` con todas las variables.
