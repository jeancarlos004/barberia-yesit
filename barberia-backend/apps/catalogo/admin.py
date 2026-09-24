from django.contrib import admin

from .models import Bloqueo, Configuracion, Horario, Servicio


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "duracion", "precio", "activo", "icono")
    list_filter = ("activo",)


@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ("dia", "abierto", "desde", "hasta")


@admin.register(Bloqueo)
class BloqueoAdmin(admin.ModelAdmin):
    list_display = ("fecha", "desde", "hasta", "motivo")


@admin.register(Configuracion)
class ConfiguracionAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not Configuracion.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
