import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.turnos.models import Turno
from apps.usuarios.models import User

print("=== USUARIOS EN BASE DE DATOS ===")
users = User.objects.all()
for user in users:
    print(f"ID: {user.id}, Email: {user.email}, Nombre: {user.nombre}, Rol: {user.rol}")

print("\n=== TURNOS EN BASE DE DATOS ===")
turnos = Turno.objects.all()
for turno in turnos:
    print(f"ID: {turno.id}, Usuario: {turno.usuario.email}, Servicio: {turno.servicio.nombre}, Fecha: {turno.fecha}, Hora: {turno.hora}, Estado: {turno.estado}")

print(f"\nTotal turnos: {turnos.count()}")
