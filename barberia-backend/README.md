# Backend Barbería YESIT

API Django + PostgreSQL (Neon) para el sistema de turnos. Las pantallas del front siguen igual; este servicio reemplaza `localStorage`.

## Requisitos

- Python 3.12+
- Cuenta [Neon](https://neon.tech) (opcional en local: si no hay `DATABASE_URL`, usa SQLite)

## Arranque local

```bash
cd barberia-backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edita `.env`: `SECRET_KEY` y, si ya tienes Neon, `DATABASE_URL`.

```bash
python manage.py migrate
python manage.py seed
python manage.py createsuperuser
python manage.py runserver 8000
```

`createsuperuser` pide email + nombre + contraseña y crea un usuario con rol `admin`.

## Endpoints

| Método | Ruta | Auth |
|---|---|---|
| POST | `/api/auth/registro/` | público |
| POST | `/api/auth/login/` | público (`email`, `password`) |
| POST | `/api/auth/refresh/` | público (`refresh`) |
| GET | `/api/auth/yo/` | JWT |
| GET/POST/PATCH/DELETE | `/api/servicios/` | GET público (activos); escritura admin |
| GET/PUT | `/api/horarios/` | GET público; PUT admin (lista de 7 días) |
| GET/POST/DELETE | `/api/bloqueos/` | GET público; escritura admin |
| GET | `/api/disponibilidad/?fecha=YYYY-MM-DD&servicio=UUID` | público |
| GET | `/api/disponibilidad/siguiente/?servicio=UUID` | JWT (Turno Express) |
| GET/POST | `/api/turnos/` | JWT (cliente: los suyos; admin: todos) |
| PATCH | `/api/turnos/{id}/` | dueño cancela; admin cambia estado |
| GET/PUT | `/api/configuracion/` | GET público; PUT admin |
| GET | `/api/admin/metricas/?fecha=` | admin |
| GET | `/api/clientes/` | admin |

Header: `Authorization: Bearer <access>`.

## Despliegue

En Render/Railway/Fly:

1. `DATABASE_URL` del pooler de Neon (`-pooler` en el host).
2. `DEBUG=False`, `SECRET_KEY` fuerte, `ALLOWED_HOSTS` y `CORS_ALLOWED_ORIGINS` con tu front.
3. `python manage.py migrate && python manage.py seed && gunicorn config.wsgi:application`

## Seguridad incluida

- Contraseñas con `set_password` (nunca texto plano)
- JWT con rotación y blacklist del refresh
- Roles `cliente` / `admin` en permisos (no solo `is_staff`)
- Disponibilidad y solapes validados en el servidor + `select_for_update`
- Throttle en login/registro
- CORS explícito, `DEBUG` y `SECRET_KEY` desde entorno
