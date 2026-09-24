from datetime import date

from django.db import transaction
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalogo.models import Servicio
from apps.usuarios.permissions import EsDuenoOAdmin, IsAdminRol

from .disponibilidad import hora_str, siguiente_cupo, slots_libres
from .models import Turno
from .serializers import TurnoEstadoSerializer, TurnoSerializer


class DisponibilidadView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        fecha_raw = request.query_params.get("fecha")
        servicio_id = request.query_params.get("servicio")
        if not fecha_raw or not servicio_id:
            raise ValidationError({"detail": "Se requieren fecha y servicio."})
        try:
            fecha = date.fromisoformat(fecha_raw)
            servicio = Servicio.objects.get(pk=servicio_id, activo=True)
        except (ValueError, Servicio.DoesNotExist) as exc:
            raise ValidationError({"detail": "Fecha o servicio inválido."}) from exc
        return Response(slots_libres(fecha, servicio.duracion))


class SiguienteDisponibilidadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        servicio_id = request.query_params.get("servicio")
        if not servicio_id:
            raise ValidationError({"detail": "Se requiere servicio."})
        try:
            servicio = Servicio.objects.get(pk=servicio_id, activo=True)
        except Servicio.DoesNotExist as exc:
            raise ValidationError({"detail": "Servicio inválido."}) from exc
        cupo = siguiente_cupo(servicio.duracion)
        if not cupo:
            return Response({"detail": "No hay cupos en los próximos 30 días."}, status=status.HTTP_404_NOT_FOUND)
        return Response(cupo)


class TurnoViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = TurnoSerializer
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_permissions(self):
        if self.action in {"partial_update", "update"}:
            return [EsDuenoOAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        qs = Turno.objects.select_related("usuario", "servicio")
        user = self.request.user
        if getattr(user, "rol", None) != "admin":
            qs = qs.filter(usuario=user)
        fecha = self.request.query_params.get("fecha")
        estado = self.request.query_params.get("estado")
        if fecha:
            qs = qs.filter(fecha=fecha)
        if estado:
            qs = qs.filter(estado=estado)
        return qs

    def perform_create(self, serializer):
        servicio = serializer.validated_data["servicio"]
        fecha = serializer.validated_data["fecha"]
        hora = serializer.validated_data["hora"]
        with transaction.atomic():
            list(
                Turno.objects.select_for_update().filter(fecha=fecha).exclude(estado=Turno.Estado.CANCELADO)
            )
            libres = slots_libres(fecha, servicio.duracion)
            if hora_str(hora) not in libres:
                raise ValidationError({"hora": "Ese horario no está disponible."})
            serializer.save(usuario=self.request.user, estado=Turno.Estado.CONFIRMADO)

    def partial_update(self, request, *args, **kwargs):
        turno = self.get_object()
        serializer = TurnoEstadoSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        nuevo = serializer.validated_data["estado"]
        user = request.user

        if getattr(user, "rol", None) != "admin":
            if nuevo != Turno.Estado.CANCELADO:
                raise PermissionDenied("Solo puedes cancelar tu turno.")
            if turno.estado in {Turno.Estado.CANCELADO, Turno.Estado.COMPLETADO}:
                raise ValidationError({"estado": "Este turno ya no se puede cancelar."})
        turno.estado = nuevo
        turno.save(update_fields=["estado"])
        return Response(TurnoSerializer(turno).data)


class MetricasView(APIView):
    permission_classes = [IsAdminRol]

    def get(self, request):
        raw = request.query_params.get("fecha")
        try:
            fecha = date.fromisoformat(raw) if raw else timezone_today()
        except ValueError as exc:
            raise ValidationError({"fecha": "Formato inválido, usa YYYY-MM-DD."}) from exc
        qs = Turno.objects.filter(fecha=fecha)
        return Response(
            {
                "hoy": qs.count(),
                "confirmados": qs.filter(estado=Turno.Estado.CONFIRMADO).count(),
                "pendientes": qs.filter(estado=Turno.Estado.PENDIENTE).count(),
                "cancelados": qs.filter(estado=Turno.Estado.CANCELADO).count(),
            }
        )


def timezone_today():
    from django.utils import timezone

    return timezone.localdate()
