# Lugar único para inyección de dependencias (repositorios, servicios, etc.)
# Se completa a medida que se implementan los casos de uso con MySQL.

from app.infra.mysql.conexion import obtener_conexion

# Placeholder: acá se instancian los adaptadores MySQL y se inyectan en los casos de uso.
DB = obtener_conexion
