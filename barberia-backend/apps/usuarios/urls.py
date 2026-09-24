from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import LoginView, RefreshView, RegistroView, YoView

urlpatterns = [
    path("registro/", RegistroView.as_view(), name="registro"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshView.as_view(), name="refresh"),
    path("yo/", YoView.as_view(), name="yo"),
]
