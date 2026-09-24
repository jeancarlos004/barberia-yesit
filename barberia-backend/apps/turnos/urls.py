from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import DisponibilidadView, MetricasView, SiguienteDisponibilidadView, TurnoViewSet

router = DefaultRouter()
router.register("turnos", TurnoViewSet, basename="turnos")

urlpatterns = [
    path("disponibilidad/", DisponibilidadView.as_view(), name="disponibilidad"),
    path("disponibilidad/siguiente/", SiguienteDisponibilidadView.as_view(), name="disponibilidad-siguiente"),
    path("admin/metricas/", MetricasView.as_view(), name="admin-metricas"),
    *router.urls,
]
