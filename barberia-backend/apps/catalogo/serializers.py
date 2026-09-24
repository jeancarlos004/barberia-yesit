from rest_framework import serializers

from .models import Bloqueo, Configuracion, Horario, Servicio


class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = ("id", "nombre", "duracion", "precio", "activo", "icono")

    def validate_duracion(self, value):
        if value < 15 or value > 240:
            raise serializers.ValidationError("La duración debe estar entre 15 y 240 minutos.")
        return value

    def validate_precio(self, value):
        if value < 0:
            raise serializers.ValidationError("El precio no puede ser negativo.")
        return value


class HorarioSerializer(serializers.ModelSerializer):
    desde = serializers.TimeField(format="%H:%M", input_formats=["%H:%M", "%H:%M:%S"])
    hasta = serializers.TimeField(format="%H:%M", input_formats=["%H:%M", "%H:%M:%S"])

    class Meta:
        model = Horario
        fields = ("dia", "abierto", "desde", "hasta")

    def validate_dia(self, value):
        if value < 0 or value > 6:
            raise serializers.ValidationError("El día debe estar entre 0 y 6.")
        return value


class HorariosBulkSerializer(serializers.Serializer):
    horarios = HorarioSerializer(many=True)

    def validate_horarios(self, value):
        dias = [h["dia"] for h in value]
        if len(dias) != 7 or set(dias) != set(range(7)):
            raise serializers.ValidationError("Debes enviar exactamente los 7 días (0 a 6), sin repetir.")
        return value

    def save(self, **kwargs):
        saved = []
        for item in self.validated_data["horarios"]:
            obj, _ = Horario.objects.update_or_create(dia=item["dia"], defaults=item)
            saved.append(obj)
        return saved


class BloqueoSerializer(serializers.ModelSerializer):
    desde = serializers.TimeField(format="%H:%M", input_formats=["%H:%M", "%H:%M:%S"])
    hasta = serializers.TimeField(format="%H:%M", input_formats=["%H:%M", "%H:%M:%S"])

    class Meta:
        model = Bloqueo
        fields = ("id", "fecha", "desde", "hasta", "motivo")
        read_only_fields = ("id",)


class ConfiguracionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Configuracion
        fields = ("nombre", "telefono", "direccion", "descripcion")
