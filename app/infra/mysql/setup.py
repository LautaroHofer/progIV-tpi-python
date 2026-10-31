from app.infra.mysql.conexion import obtener_conexion

TABLAS = [
    """
    CREATE TABLE IF NOT EXISTS sucursales (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        direccion TEXT,
        zona_horaria VARCHAR(50) NOT NULL DEFAULT 'America/Argentina/Buenos_Aires',
        creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB;
    """,
    """
    CREATE TABLE IF NOT EXISTS salas (
        id INT AUTO_INCREMENT PRIMARY KEY,
        sucursal_id INT NOT NULL,
        nombre VARCHAR(100) NOT NULL,
        capacidad INT NOT NULL DEFAULT 1,
        creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sucursal_id) REFERENCES sucursales(id)
    ) ENGINE=InnoDB;
    """,
    """
    CREATE TABLE IF NOT EXISTS profesores (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        email VARCHAR(150),
        creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB;
    """,
    """
    CREATE TABLE IF NOT EXISTS planes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        cantidad_clases INT NOT NULL,
        precio DECIMAL(10,2) NOT NULL,
        vigencia_meses INT NOT NULL DEFAULT 1,
        creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB;
    """,
    """
    CREATE TABLE IF NOT EXISTS alumnos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        email VARCHAR(150) UNIQUE NOT NULL,
        creditos INT NOT NULL DEFAULT 0,
        creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB;
    """,
    """
    CREATE TABLE IF NOT EXISTS clases (
        id INT AUTO_INCREMENT PRIMARY KEY,
        sala_id INT NOT NULL,
        profesor_id INT NOT NULL,
        actividad VARCHAR(100) NOT NULL,
        fecha_inicio TIMESTAMP NOT NULL,
        fecha_fin TIMESTAMP NOT NULL,
        cupo INT NOT NULL DEFAULT 1,
        recurrente BOOLEAN DEFAULT FALSE,
        clase_recurrente_id INT NULL,
        creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sala_id) REFERENCES salas(id),
        FOREIGN KEY (profesor_id) REFERENCES profesores(id)
    ) ENGINE=InnoDB;
    """,
    """
    CREATE TABLE IF NOT EXISTS reservas (
        id INT AUTO_INCREMENT PRIMARY KEY,
        alumno_id INT NOT NULL,
        clase_id INT NOT NULL,
        estado VARCHAR(30) NOT NULL DEFAULT 'confirmada',
        fecha_reserva TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        credito_descontado BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (alumno_id) REFERENCES alumnos(id),
        FOREIGN KEY (clase_id) REFERENCES clases(id)
    ) ENGINE=InnoDB;
    """,
    """
    CREATE TABLE IF NOT EXISTS creditos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        alumno_id INT NOT NULL,
        cantidad INT NOT NULL,
        tipo VARCHAR(20) NOT NULL,
        motivo TEXT,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (alumno_id) REFERENCES alumnos(id)
    ) ENGINE=InnoDB;
    """,
    """
    CREATE TABLE IF NOT EXISTS lista_espera (
        id INT AUTO_INCREMENT PRIMARY KEY,
        clase_id INT NOT NULL,
        alumno_id INT NOT NULL,
        posicion INT NOT NULL,
        creada_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        confirmada_en TIMESTAMP NULL,
        FOREIGN KEY (clase_id) REFERENCES clases(id),
        FOREIGN KEY (alumno_id) REFERENCES alumnos(id)
    ) ENGINE=InnoDB;
    """,
    """
    CREATE TABLE IF NOT EXISTS configuracion (
        clave VARCHAR(100) PRIMARY KEY,
        valor TEXT NOT NULL
    ) ENGINE=InnoDB;
    """,
]


def setup():
    conn = obtener_conexion()
    try:
        with conn.cursor() as cur:
            for tabla in TABLAS:
                cur.execute(tabla)
            cur.execute(
                """
                INSERT INTO configuracion (clave, valor)
                VALUES ('ventana_cancelacion_horas', '4')
                ON DUPLICATE KEY UPDATE valor = VALUES(valor)
                """
            )
        conn.commit()
        print("Tablas MySQL creadas correctamente.")
    finally:
        conn.close()


if __name__ == "__main__":
    setup()
