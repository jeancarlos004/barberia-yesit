from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import BloqueoViewSet, ConfiguracionView, HorarioView, ServicioViewSet

router = DefaultRouter()
router.register("servicios", ServicioViewSet, basename="servicios")
router.register("bloqueos", BloqueoViewSet, basename="bloqueos")

urlpatterns = [
    path("horarios/", HorarioView.as_view(), name="horarios"),
    path("configuracion/", ConfiguracionView.as_view(), name="configuracion"),
    *router.urls,
]
