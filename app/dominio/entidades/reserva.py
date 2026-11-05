# Entidad: Reserva

class Reserva:
    def __init__(self, id, alumno_id, clase_id, estado="confirmada", fecha_reserva=None):
        self.id = id
        self.alumno_id = alumno_id
        self.clase_id = clase_id
        self.estado = estado
        self.fecha_reserva = fecha_reserva
