from app.infra.db.conexion import obtener_conexion

def setup():
    conn = obtener_conexion()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sucursales (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    direccion TEXT,
                    creado_en TIMESTAMP DEFAULT NOW()
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS salas (
                    id SERIAL PRIMARY KEY,
                    sucursal_id INTEGER REFERENCES sucursales(id),
                    nombre VARCHAR(100) NOT NULL,
                    capacidad INTEGER NOT NULL DEFAULT 1,
                    creado_en TIMESTAMP DEFAULT NOW()
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS profesores (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    email VARCHAR(150),
                    creado_en TIMESTAMP DEFAULT NOW()
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS alumnos (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    email VARCHAR(150) UNIQUE NOT NULL,
                    creditos INTEGER NOT NULL DEFAULT 0,
                    creado_en TIMESTAMP DEFAULT NOW()
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS reservas (
                    id SERIAL PRIMARY KEY,
                    alumno_id INTEGER REFERENCES alumnos(id),
                    clase_id INTEGER,
                    estado VARCHAR(30) NOT NULL DEFAULT 'confirmada',
                    fecha_reserva TIMESTAMP DEFAULT NOW()
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS configuracion (
                    clave VARCHAR(100) PRIMARY KEY,
                    valor TEXT NOT NULL
                );
            """)
            cur.execute("""
                INSERT INTO configuracion (clave, valor)
                VALUES ('ventana_cancelacion_horas', '4')
                ON CONFLICT (clave) DO NOTHING;
            """)
        conn.commit()
        print("Tablas creadas correctamente.")
    finally:
        conn.close()

if __name__ == "__main__":
    setup()
