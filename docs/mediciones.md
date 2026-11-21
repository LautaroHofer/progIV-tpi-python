# Informe de medición de la tarea pesada

## Hipótesis
La ejecución de la tarea pesada en su versión final no degrada la latencia de los endpoints livianos (`/health`) ni bloquea la atención de reservas concurrentes.

## Metodología
1. Se escribió la hipótesis con un número antes de correr nada.
2. Se dejó el sistema en un estado conocido: base cargada con el mismo volumen en las dos corridas, nada más corriendo en la máquina.
3. Se generó carga sostenida sobre el endpoint de generación de grilla durante al menos 30 segundos, registrando la línea de base sin la tarea pesada.
4. Se repitió con la tarea pesada corriendo, primero en la versión ingenua y después en la versión final.
5. Se repitió cada escenario al menos tres veces y se registraron las tres.
6. Se anotaron los números con unidades, no capturas de pantalla sin contexto.

## Resultados

| Escenario | p50 (ms) | p95 (ms) | p99 (ms) | Req/s | Memoria (MB) |
|-----------|----------|----------|----------|-------|--------------|
| Línea de base (sin tarea) | - | - | - | - | - |
| Versión ingenua | - | - | - | - | - |
| Versión final | - | - | - | - | - |

## Herramientas utilizadas
- [ ] `locust`
- [ ] `k6`
- [ ] `autocannon`
- [ ] Otra: _______________

## Conclusión
A completar luego de correr las pruebas de carga.
