from rest_framework import generics, permissions, status, throttling, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import User
from .permissions import IsAdminRol
from .serializers import LoginSerializer, RegistroSerializer, UserPublicSerializer


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


class ClienteViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserPublicSerializer
    permission_classes = [IsAdminRol]

    def get_queryset(self):
        return User.objects.filter(rol=User.Rol.CLIENTE)
