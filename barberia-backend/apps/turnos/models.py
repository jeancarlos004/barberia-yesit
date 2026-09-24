import uuid

from django.db import models
from django.db.models import Q, UniqueConstraint


class Turno(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        CONFIRMADO = "confirmado", "Confirmado"
        COMPLETADO = "completado", "Completado"
        CANCELADO = "cancelado", "Cancelado"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey("usuarios.User", on_delete=models.CASCADE, related_name="turnos")
    servicio = models.ForeignKey("catalogo.Servicio", on_delete=models.PROTECT, related_name="turnos")
    fecha = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.CONFIRMADO)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "-hora"]
        constraints = [
            UniqueConstraint(
                fields=["fecha", "hora"],
                condition=~Q(estado="cancelado"),
                name="uniq_turno_activo_fecha_hora",
            )
        ]
        indexes = [
            models.Index(fields=["fecha", "estado"]),
            models.Index(fields=["usuario", "fecha"]),
        ]

    def __str__(self):
        return f"{self.fecha} {self.hora} ({self.estado})"
