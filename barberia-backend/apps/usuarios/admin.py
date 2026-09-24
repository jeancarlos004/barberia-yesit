from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User
    list_display = ("email", "nombre", "rol", "is_active", "is_staff")
    list_filter = ("rol", "is_active", "is_staff")
    ordering = ("email",)
    search_fields = ("email", "nombre", "telefono")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Perfil", {"fields": ("nombre", "telefono", "rol")}),
        ("Permisos", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "nombre", "telefono", "rol", "password1", "password2"),
            },
        ),
    )
