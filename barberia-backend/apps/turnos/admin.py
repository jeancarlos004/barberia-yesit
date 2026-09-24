from django.contrib import admin

from .models import Turno


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ("fecha", "hora", "usuario", "servicio", "estado")
    list_filter = ("estado", "fecha")
    search_fields = ("usuario__email", "usuario__nombre")
