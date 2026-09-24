from datetime import date

from rest_framework import mixins, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.usuarios.permissions import IsAdminRol

from .models import Bloqueo, Configuracion, Horario, Servicio
from .serializers import (
    BloqueoSerializer,
    ConfiguracionSerializer,
    HorarioSerializer,
    HorariosBulkSerializer,
    ServicioSerializer,
)


class ServicioViewSet(viewsets.ModelViewSet):
    serializer_class = ServicioSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        qs = Servicio.objects.all()
        user = self.request.user
        if user.is_authenticated and getattr(user, "rol", None) == "admin":
            return qs
        return qs.filter(activo=True)

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [permissions.AllowAny()]
        return [IsAdminRol()]


class HorarioView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [IsAdminRol()]

    def get(self, request):
        return Response(HorarioSerializer(Horario.objects.all(), many=True).data)

    def put(self, request):
        payload = request.data
        if isinstance(payload, list):
            payload = {"horarios": payload}
        serializer = HorariosBulkSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        saved = serializer.save()
        return Response(HorarioSerializer(saved, many=True).data)


class BloqueoViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = BloqueoSerializer

    def get_queryset(self):
        qs = Bloqueo.objects.filter(fecha__gte=date.today())
        return qs

    def get_permissions(self):
        if self.action == "list":
            return [permissions.AllowAny()]
        return [IsAdminRol()]


class ConfiguracionView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [IsAdminRol()]

    def get(self, request):
        return Response(ConfiguracionSerializer(Configuracion.get_solo()).data)

    def put(self, request):
        obj = Configuracion.get_solo()
        serializer = ConfiguracionSerializer(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
