from datetime import time

from django.core.management.base import BaseCommand

from apps.catalogo.models import Configuracion, Horario, Servicio


SERVICIOS = [
    {"nombre": "Corte clásico", "duracion": 30, "precio": 20000, "icono": Servicio.Icono.SCISSORS},
    {"nombre": "Corte + barba", "duracion": 45, "precio": 30000, "icono": Servicio.Icono.COMBO},
    {"nombre": "Barba", "duracion": 20, "precio": 15000, "icono": Servicio.Icono.BEARD},
    {"nombre": "Corte premium", "duracion": 60, "precio": 40000, "icono": Servicio.Icono.CROWN},
]


class Command(BaseCommand):
    help = "Crea servicios, horarios y configuración inicial de Barberia YESIT."

    def handle(self, *args, **options):
        for data in SERVICIOS:
            Servicio.objects.get_or_create(nombre=data["nombre"], defaults={**data, "activo": True})

        # 0 domingo … 6 sábado
        for dia in range(7):
            abierto = dia != 0
            Horario.objects.update_or_create(
                dia=dia,
                defaults={
                    "abierto": abierto,
                    "desde": time(8, 0),
                    "hasta": time(19, 0),
                },
            )

        Configuracion.get_solo()
        self.stdout.write(self.style.SUCCESS("Catálogo inicial listo."))
