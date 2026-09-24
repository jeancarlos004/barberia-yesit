from django.test import TestCase
from rest_framework.test import APIClient

from apps.usuarios.models import User


class AuthTests(TestCase):
    def test_registro_hashea_password_y_devuelve_jwt(self):
        client = APIClient()
        res = client.post(
            "/api/auth/registro/",
            {
                "email": "nuevo@barberia.com",
                "password": "ClaveSegura1",
                "nombre": "Luis",
                "telefono": "3001112233",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        self.assertIn("access", res.data)
        user = User.objects.get(email="nuevo@barberia.com")
        self.assertTrue(user.check_password("ClaveSegura1"))
        self.assertNotEqual(user.password, "ClaveSegura1")
        self.assertEqual(user.rol, User.Rol.CLIENTE)

    def test_login_con_email(self):
        User.objects.create_user(
            email="ana@barberia.com", password="ClaveSegura1", nombre="Ana"
        )
        client = APIClient()
        res = client.post(
            "/api/auth/login/",
            {"email": "ana@barberia.com", "password": "ClaveSegura1"},
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("access", res.data)
        self.assertEqual(res.data["user"]["rol"], "cliente")
