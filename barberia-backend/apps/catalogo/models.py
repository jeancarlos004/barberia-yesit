import uuid
from datetime import time

from django.core.exceptions import ValidationError
from django.db import models


class Servicio(models.Model):
    class Icono(models.TextChoices):
        SCISSORS = "scissors", "Tijeras"
        BEARD = "beard", "Barba"
        COMBO = "combo", "Combo"
        CROWN = "crown", "Premium"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    duracion = models.PositiveIntegerField(help_text="Minutos")
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)
    icono = models.CharField(max_length=20, choices=Icono.choices, default=Icono.SCISSORS)

    class Meta:
        ordering = ["precio", "nombre"]

    def __str__(self):
        return self.nombre


class Horario(models.Model):
    dia = models.PositiveSmallIntegerField(unique=True)
    abierto = models.BooleanField(default=True)
    desde = models.TimeField(default=time(8, 0))
    hasta = models.TimeField(default=time(19, 0))

    class Meta:
        ordering = ["dia"]

    def clean(self):
        if self.dia > 6:
            raise ValidationError({"dia": "El día debe estar entre 0 (domingo) y 6 (sábado)."})
        if self.abierto and self.desde >= self.hasta:
            raise ValidationError("La hora de apertura debe ser anterior al cierre.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Día {self.dia}"


class Bloqueo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fecha = models.DateField()
    desde = models.TimeField()
    hasta = models.TimeField()
    motivo = models.CharField(max_length=200)

    class Meta:
        ordering = ["fecha", "desde"]

    def clean(self):
        if self.desde >= self.hasta:
            raise ValidationError("El inicio del bloqueo debe ser anterior al fin.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.fecha} {self.motivo}"


class Configuracion(models.Model):
    SINGLETON_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=120, default="BARBERIA YESIT")
    telefono = models.CharField(max_length=40, default="+57 300 123 4567")
    direccion = models.CharField(max_length=200, default="Calle 13 #10-20")
    descripcion = models.TextField(
        default="Cortes clásicos y modernos, arreglo de barba y atención de primera."
    )

    class Meta:
        verbose_name_plural = "Configuración"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(
            pk=cls.SINGLETON_ID,
            defaults={
                "nombre": "BARBERIA YESIT",
                "telefono": "+57 300 123 4567",
                "direccion": "Calle 13 #10-20",
                "descripcion": "Cortes clásicos y modernos, arreglo de barba y atención de primera.",
            },
        )
        return obj

    def save(self, *args, **kwargs):
        self.pk = self.SINGLETON_ID
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre
