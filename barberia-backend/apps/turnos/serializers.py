from rest_framework import serializers

from apps.catalogo.models import Servicio

from .models import Turno


class TurnoSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source="usuario.nombre", read_only=True)
    servicio_nombre = serializers.CharField(source="servicio.nombre", read_only=True)
    hora = serializers.TimeField(format="%H:%M", input_formats=["%H:%M", "%H:%M:%S"])

    class Meta:
        model = Turno
        fields = (
            "id",
            "usuario",
            "cliente_nombre",
            "servicio",
            "servicio_nombre",
            "fecha",
            "hora",
            "estado",
            "creado",
        )
        read_only_fields = ("id", "usuario", "estado", "creado")

    def validate_servicio(self, value: Servicio):
        if not value.activo:
            raise serializers.ValidationError("Ese servicio no está disponible.")
        return value


class TurnoEstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Turno
        fields = ("estado",)
