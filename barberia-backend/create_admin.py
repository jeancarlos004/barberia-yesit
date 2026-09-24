import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.usuarios.models import User

if not User.objects.filter(email='admin@barberia.com').exists():
    admin = User.objects.create_superuser(
        email='admin@barberia.com',
        nombre='Admin',
        password='Admin123'
    )
    print(f"Admin user created: {admin.email}")
else:
    print("Admin user already exists")
