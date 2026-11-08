# Caso de uso: Reservar turno

class ReservarTurno:
    def __init__(self, reserva_repo):
        self.reserva_repo = reserva_repo

    def ejecutar(self, alumno_id, clase_id):
        return self.reserva_repo.crear({
            "alumno_id": alumno_id,
            "clase_id": clase_id,
            "estado": "confirmada"
        })
