from datetime import date, time

from django.test import TestCase

from apps.catalogo.models import Bloqueo, Horario, Servicio
from apps.turnos.disponibilidad import slots_libres, weekday_domingo_cero
from apps.turnos.models import Turno
from apps.usuarios.models import User


class DisponibilidadTests(TestCase):
    def setUp(self):
        for dia in range(7):
            Horario.objects.create(
                dia=dia,
                abierto=dia != 0,
                desde=time(8, 0),
                hasta=time(19, 0),
            )
        self.servicio = Servicio.objects.create(
            nombre="Corte clásico", duracion=30, precio=20000, icono="scissors"
        )
        self.user = User.objects.create_user(
            email="cliente@test.com", password="secreto1234", nombre="Ana"
        )

    def test_domingo_sin_cupos(self):
        d = date(2026, 9, 20)
        self.assertEqual(weekday_domingo_cero(d), 0)
        self.assertEqual(slots_libres(d, 30), [])

    def test_bloqueo_y_turno_quitan_solape(self):
        lunes = date(2026, 9, 21)
        self.assertEqual(weekday_domingo_cero(lunes), 1)
        Bloqueo.objects.create(fecha=lunes, desde=time(8, 0), hasta=time(9, 0), motivo="Reunión")
        Turno.objects.create(
            usuario=self.user,
            servicio=self.servicio,
            fecha=lunes,
            hora=time(10, 0),
            estado=Turno.Estado.CONFIRMADO,
        )
        huecos = slots_libres(lunes, 30)
        self.assertNotIn("08:00", huecos)
        self.assertNotIn("08:30", huecos)
        self.assertNotIn("10:00", huecos)
        self.assertIn("09:00", huecos)
        self.assertIn("10:30", huecos)
