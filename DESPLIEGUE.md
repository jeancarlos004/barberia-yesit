# Guía de Despliegue - Barbería YESIT

## Arquitectura de Despliegue Objetivo

```
                  INTERNET
                     │
                     ▼
        ┌─────────────────────────┐
        │       Vercel            │
        │   React + Vite          │
        │   Frontend GRATIS       │
        └────────────┬────────────┘
                     │ HTTPS
                     ▼
        ┌─────────────────────────┐
        │        Render           │
        │ Django + Gunicorn       │
        │ Backend GRATIS          │
        └────────────┬────────────┘
                     │
                     ▼
        ┌─────────────────────────┐
        │         Neon            │
        │       PostgreSQL        │
        │       Free tier         │
        └─────────────────────────┘
```

## Estado Actual
✅ Backend Django configurado y funcionando localmente
✅ Frontend React conectado con el backend
✅ Base de datos Neon configurada y funcionando
✅ Usuario admin creado (admin@barberia.com / Admin123)
✅ Archivos de configuración para despliegue creados

## Paso 1: Desplegar Backend en Render

### 1.1 Preparar Repositorio en GitHub
1. Sube tu proyecto a GitHub (incluyendo `barberia-backend/`)
2. Asegúrate de incluir los archivos creados:
   - `render.yaml`
   - `build.sh`
   - `requirements.txt` (actualizado con whitenoise)

### 1.2 Crear cuenta en Render
1. Ve a [render.com](https://render.com) y crea una cuenta gratuita
2. Conecta tu cuenta de GitHub

### 1.3 Desplegar Backend Django
1. En Render, crea un "New Web Service"
2. Conecta tu repositorio de GitHub
3. Configura los siguientes parámetros:

**Basic Settings:**
- Name: `barberia-backend`
- Region: Oregon (o el más cercano a ti)
- Branch: `main`

**Build & Deploy:**
- Runtime: `Python 3`
- Build Command: `pip install -r requirements.txt && python manage.py migrate --noinput && python manage.py seed`
- Start Command: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`

**Environment Variables:**
```
SECRET_KEY= (genera una clave fuerte aleatoria)
DEBUG=False
ALLOWED_HOSTS=barberia-backend.onrender.com
CORS_ALLOWED_ORIGINS=https://barberia-frontend.vercel.app
DATABASE_URL=postgresql://neondb_owner:npg_5euEYOmS9TaL@ep-fragrant-fire-b5xfp6gf-pooler.c-7.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

4. Haz clic en "Create Web Service"
5. Espera a que termine el despliegue (aprox. 5-10 minutos)
6. Copia la URL generada (ej: `https://barberia-backend.onrender.com`)

## Paso 2: Desplegar Frontend en Vercel

### 2.1 Preparar Repositorio
1. Asegúrate de que `quick-cut-scheduling-main/` esté en GitHub
2. Incluye el archivo `vercel.json` creado

### 2.2 Crear cuenta en Vercel
1. Ve a [vercel.com](https://vercel.com) y crea una cuenta gratuita
2. Conecta tu cuenta de GitHub

### 2.3 Desplegar Frontend React
1. En Vercel, haz clic en "Add New Project"
2. Selecciona tu repositorio `quick-cut-scheduling-main`
3. Configura los siguientes parámetros:

**Framework Preset:** Vite
**Root Directory:** `quick-cut-scheduling-main` (o dejar vacío si es la raíz)

**Environment Variables:**
```
VITE_API_URL=https://barberia-backend.onrender.com
```

4. Haz clic en "Deploy"
5. Espera a que termine el despliegue (aprox. 2-3 minutos)
6. Copia la URL generada (ej: `https://barberia-frontend.vercel.app`)

## Paso 3: Actualizar Configuración CORS

Una vez que tengas las URLs de producción:

### 3.1 Actualizar Backend en Render
1. Ve a tu Web Service en Render
2. En "Environment", actualiza:
   - `ALLOWED_HOSTS`: añade tu URL de Vercel
   - `CORS_ALLOWED_ORIGINS`: añade tu URL de Vercel

Ejemplo:
```
ALLOWED_HOSTS=barberia-backend.onrender.com,barberia-frontend.vercel.app
CORS_ALLOWED_ORIGINS=https://barberia-frontend.vercel.app
```

### 3.2 Actualizar Frontend en Vercel
1. Ve a tu proyecto en Vercel
2. En "Settings > Environment Variables"
3. Actualiza `VITE_API_URL` con la URL de tu backend en Render

## Paso 4: Verificar Despliegue

### 4.1 Verificar Backend
```bash
curl https://barberia-backend.onrender.com/api/servicios/
```

Deberías ver la lista de servicios en JSON.

### 4.2 Verificar Frontend
1. Abre tu URL de Vercel en el navegador
2. Intenta registrarte como nuevo usuario
3. Intenta hacer login con `admin@barberia.com` / `Admin123`
4. Verifica que puedas ver los servicios y hacer reservas

## Paso 5: Configurar Dominio Personalizado (Opcional)

### En Vercel:
1. Ve a "Settings > Domains"
2. Añade tu dominio personal (ej: `barberia.com`)
3. Sigue las instrucciones para configurar DNS

### En Render:
1. Ve a "Settings > Custom Domains"
2. Añade tu subdominio (ej: `api.barberia.com`)
3. Sigue las instrucciones para configurar DNS

## Credenciales de Admin

- Email: `admin@barberia.com`
- Contraseña: `Admin123`

**IMPORTANTE:** Cambia estas credenciales en producción:
1. Entra al admin de Django: `https://barberia-backend.onrender.com/admin/`
2. Cambia la contraseña del usuario admin

## Archivos de Configuración Creados

### Backend (barberia-backend/):
- `render.yaml` - Configuración automática de despliegue en Render
- `build.sh` - Script de build para migraciones y seed
- `requirements.txt` - Actualizado con whitenoise para archivos estáticos
- `.env.production` - Variables de entorno para producción

### Frontend (quick-cut-scheduling-main/):
- `vercel.json` - Configuración automática de despliegue en Vercel
- `.env.production` - Variables de entorno para producción

## Pruebas Locales

Para probar el sistema localmente:

```bash
# Terminal 1 - Backend
cd barberia-backend
.venv/Scripts/activate
python manage.py runserver 8000

# Terminal 2 - Frontend
cd quick-cut-scheduling-main
npm run dev
```

El frontend estará en `http://localhost:8080` y el backend en `http://127.0.0.1:8000`

## URLs de Endpoints

- POST `/api/auth/registro/` - Registro de usuarios
- POST `/api/auth/login/` - Login
- GET `/api/servicios/` - Listar servicios
- GET `/api/horarios/` - Horarios de atención
- GET `/api/disponibilidad/?fecha=YYYY-MM-DD&servicio=UUID` - Disponibilidad
- POST `/api/turnos/` - Crear turno
- GET `/api/turnos/` - Listar turnos (requiere auth)
- PATCH `/api/turnos/{id}/` - Cancelar turno
- GET `/api/configuracion/` - Configuración del negocio

## Beneficios de esta Arquitectura

**Vercel (Frontend):**
- Despliegue instantáneo
- CDN global
- Preview deployments
- Edge functions
- SSL automático
- Dominios gratuitos

**Render (Backend):**
- Soporte nativo de Django
- Integración con GitHub
- Logs en tiempo real
- Escalado automático
- SSL automático
- Gratis para uso personal

**Neon (Base de datos):**
- PostgreSQL serverless
- Escalado automático
- Branching de base de datos
- Time travel queries
- Gratis hasta 0.5GB

## Troubleshooting

### Si el frontend no se conecta al backend:
1. Verifica que `CORS_ALLOWED_ORIGINS` incluya la URL de Vercel
2. Verifica que `VITE_API_URL` sea correcta en Vercel
3. Revisa los logs en Render y Vercel

### Si hay errores de migración:
1. Revisa los logs de build en Render
2. Verifica que la conexión a Neon funcione
3. Ejecuta manualmente `python manage.py migrate` si es necesario

### Si el admin no funciona:
1. Verifica que el usuario admin exista en la base de datos de Neon
2. Intenta crear un nuevo superusuario desde el backend local y sincronizar
