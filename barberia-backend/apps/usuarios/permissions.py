from rest_framework.permissions import BasePermission


class IsAdminRol(BasePermission):
    message = "Se requiere rol de administrador."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, "rol", None) == "admin")


class EsDuenoOAdmin(BasePermission):
    message = "No puedes modificar este turno."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if getattr(user, "rol", None) == "admin":
            return True
        return getattr(obj, "usuario_id", None) == user.id
