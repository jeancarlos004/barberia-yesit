from datetime import timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from rest_framework import generics, permissions, status, throttling, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
import google.oauth2.id_token
from google.auth.transport import requests as google_requests

from .models import User, PasswordResetToken
from .permissions import IsAdminRol
from .serializers import (
    LoginSerializer,
    RegistroSerializer,
    UserPublicSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)


class AuthBurstThrottle(throttling.ScopedRateThrottle):
    scope = "auth"


class RegistroView(generics.CreateAPIView):
    serializer_class = RegistroSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AuthBurstThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = LoginSerializer.get_token(user)
        return Response(
            {
                "access": str(tokens.access_token),
                "refresh": str(tokens),
                "user": UserPublicSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AuthBurstThrottle]


class RefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AuthBurstThrottle]


class YoView(APIView):
    def get(self, request):
        return Response(UserPublicSerializer(request.user).data)


class ClienteViewSet(viewsets.ModelViewSet):
    serializer_class = UserPublicSerializer
    permission_classes = [IsAdminRol]

    def get_queryset(self):
        return User.objects.filter(rol=User.Rol.CLIENTE)

    @action(detail=True, methods=['post'])
    def bloquear(self, request, pk=None):
        cliente = self.get_object()
        cliente.is_active = False
        cliente.save()
        return Response({'message': 'Cliente bloqueado correctamente'})

    @action(detail=True, methods=['post'])
    def desbloquear(self, request, pk=None):
        cliente = self.get_object()
        cliente.is_active = True
        cliente.save()
        return Response({'message': 'Cliente desbloqueado correctamente'})

    @action(detail=True, methods=['post'])
    def cambiar_rol(self, request, pk=None):
        cliente = self.get_object()
        nuevo_rol = request.data.get('rol')
        if nuevo_rol not in [User.Rol.CLIENTE, User.Rol.ADMIN]:
            return Response(
                {'error': 'Rol inválido. Debe ser cliente o admin'},
                status=status.HTTP_400_BAD_REQUEST
            )
        cliente.rol = nuevo_rol
        cliente.save()
        return Response({'message': f'Rol cambiado a {nuevo_rol} correctamente'})


class PasswordResetRequestView(generics.CreateAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AuthBurstThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        
        user = User.objects.get(email__iexact=email)
        
        # Eliminar tokens anteriores no usados
        PasswordResetToken.objects.filter(user=user, used=False).delete()
        
        # Crear nuevo token
        token = PasswordResetToken.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        # Construir URL de reset
        frontend_url = settings.CORS_ALLOWED_ORIGINS[0] if settings.CORS_ALLOWED_ORIGINS else "http://localhost:8080"
        reset_url = f"{frontend_url}/reset-password?token={token.token}"
        
        # Enviar email
        subject = "Restablecer tu contraseña - Barbería YESIT"
        message = render_to_string(
            "email/recuperar_password.html",
            {"user": user, "reset_url": reset_url}
        )
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=message,
                fail_silently=False
            )
        except Exception as e:
            # En desarrollo, imprimir en consola
            print(f"Email reset URL: {reset_url}")
            print(f"Error enviando email: {e}")
        
        return Response(
            {"message": "Se ha enviado un correo con las instrucciones para restablecer tu contraseña"},
            status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(generics.CreateAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AuthBurstThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        reset_token = serializer.validated_data["reset_token"]
        new_password = serializer.validated_data["new_password"]
        
        # Actualizar contraseña
        reset_token.user.set_password(new_password)
        reset_token.user.save()
        
        # Marcar token como usado
        reset_token.used = True
        reset_token.save()
        
        return Response(
            {"message": "Contraseña restablecida exitosamente"},
            status=status.HTTP_200_OK
        )


class GoogleOAuthValidateView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AuthBurstThrottle]

    def create(self, request, *args, **kwargs):
        credential = request.data.get("credential")
        
        if not credential:
            return Response(
                {"error": "Se requiere el credential de Google"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar ID Token con google-auth
        try:
            idinfo = google.oauth2.id_token.verify_oauth2_token(
                credential,
                google_requests.Request(),
                audience=settings.GOOGLE_OAUTH2_CLIENT_ID
            )
        except ValueError as e:
            return Response(
                {"error": "Token de Google inválido o expirado"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validaciones adicionales del token
        if idinfo.get("iss") != "accounts.google.com":
            return Response(
                {"error": "Issuer de Google inválido"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not idinfo.get("email_verified", False):
            return Response(
                {"error": "Email de Google no verificado"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        email = idinfo.get("email")
        if not email:
            return Response(
                {"error": "Email no proporcionado por Google"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Buscar usuario por email
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            # Usuario nuevo - crear cuenta
            given_name = idinfo.get("given_name", "")
            family_name = idinfo.get("family_name", "")
            nombre = f"{given_name} {family_name}".strip() or email.split("@")[0]
            
            user = User.objects.create_user(
                email=email,
                password=None,  # Será set_unusable_password
                nombre=nombre,
                telefono="",
                rol=User.Rol.CLIENTE
            )
            user.set_unusable_password()
            user.save()
        else:
            # Usuario existe - verificar si tiene password usable
            if user.has_usable_password():
                return Response(
                    {"error": "Ya existe una cuenta con este correo. Utiliza email y contraseña para iniciar sesión."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Usuario sin password usable (usuario Google) - permitir login sin modificar datos
        
        # Generar JWT propios de Django
        from .serializers import LoginSerializer
        tokens = LoginSerializer.get_token(user)
        
        return Response(
            {
                "access": str(tokens.access_token),
                "refresh": str(tokens),
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "nombre": user.nombre,
                    "telefono": user.telefono,
                    "rol": user.rol,
                    "is_active": user.is_active,
                    "date_joined": user.date_joined.isoformat(),
                }
            },
            status=status.HTTP_200_OK
        )
