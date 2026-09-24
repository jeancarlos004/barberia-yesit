import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password, nombre="", telefono="", rol="cliente", **extra):
        if not email:
            raise ValueError("El email es obligatorio")
        email = self.normalize_email(email)
        if rol not in {User.Rol.CLIENTE, User.Rol.ADMIN}:
            rol = User.Rol.CLIENTE
        user = self.model(
            email=email,
            nombre=nombre,
            telefono=telefono,
            rol=rol,
            is_staff=rol == User.Rol.ADMIN,
            **extra,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, nombre="Administrador", **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("rol", User.Rol.ADMIN)
        extra.setdefault("nombre", nombre)
        if extra.get("is_staff") is not True:
            raise ValueError("Superuser debe tener is_staff=True")
        if extra.get("is_superuser") is not True:
            raise ValueError("Superuser debe tener is_superuser=True")
        return self.create_user(email, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    class Rol(models.TextChoices):
        CLIENTE = "cliente", "Cliente"
        ADMIN = "admin", "Administrador"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField("correo", unique=True)
    nombre = models.CharField(max_length=120)
    telefono = models.CharField(max_length=30, blank=True)
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.CLIENTE)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nombre"]

    objects = UserManager()

    class Meta:
        ordering = ["nombre"]

    def save(self, *args, **kwargs):
        if self.rol == self.Rol.ADMIN:
            self.is_staff = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
