# Guía para Subir el Proyecto a GitHub

## Paso 1: Inicializar Git en el Proyecto

```bash
cd C:\Users\USUARIO\Desktop\quick-cut-scheduling-main
git init
```

## Paso 2: Crear Archivo .gitignore

Ya existe un archivo `.gitignore` en el proyecto, pero vamos a asegurarnos de que excluya los archivos correctos:

```bash
# Verificar que exista .gitignore
cat .gitignore
```

Si no existe o está incompleto, crea uno con este contenido:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.venv/
venv/
ENV/
env/

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
/static/
/media/

# Environment variables
.env
.env.local
.env.*.local

# Node
node_modules/
dist/
.npm/
.cache/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Misc
*.pyc
```

## Paso 3: Agregar Archivos al Git

```bash
git add .
```

## Paso 4: Hacer el Primer Commit

```bash
git commit -m "Initial commit: Barbería YESIT - Sistema de turnos

- Backend Django con REST API
- Frontend React con Vite
- Conexión JWT authentication
- Base de datos Neon PostgreSQL
- Configuración para despliegue Vercel + Render"
```

## Paso 5: Crear Repositorio en GitHub

1. Ve a [github.com](https://github.com) e inicia sesión
2. Haz clic en el botón "+" en la esquina superior derecha
3. Selecciona "New repository"
4. Configura el repositorio:
   - **Repository name**: `barberia-yesit` (o el nombre que prefieras)
   - **Description**: "Sistema de turnos para barbería con Django + React"
   - **Public/Private**: Elige según tu preferencia
   - **NO** marques "Initialize this repository with a README"
   - **NO** añadas .gitignore (ya tenemos uno)
   - **NO** elijas licencia (puedes añadir después)

5. Haz clic en "Create repository"

## Paso 6: Conectar Repositorio Local con GitHub

GitHub te mostrará instrucciones. Copia y ejecuta estos comandos:

```bash
git remote add origin https://github.com/TU_USUARIO/barberia-yesit.git
git branch -M main
git push -u origin main
```

**IMPORTANTE:** Reemplaza `TU_USUARIO` con tu nombre de usuario de GitHub y `barberia-yesit` con el nombre que le diste al repositorio.

## Paso 7: Verificar que Funcionó

```bash
git status
git remote -v
```

Deberías ver que el repositorio remoto está configurado correctamente.

## Estructura de Carpetas en GitHub

Tu repositorio debería tener esta estructura:

```
barberia-yesit/
├── barberia-backend/
│   ├── apps/
│   ├── config/
│   ├── .env.production
│   ├── .env.example
│   ├── build.sh
│   ├── manage.py
│   ├── render.yaml
│   ├── requirements.txt
│   └── ...
├── quick-cut-scheduling-main/
│   ├── src/
│   ├── public/
│   ├── vercel.json
│   ├── package.json
│   ├── .env.production
│   └── ...
├── DESPLIEGUE.md
├── GIT_SETUP.md
└── .gitignore
```

## Solución de Problemas Comunes

### Error: "fatal: not a git repository"
Solución: Ejecuta `git init` en la carpeta raíz del proyecto.

### Error: "Permission denied (publickey)"
Solución: Necesitas configurar SSH keys en GitHub o usar HTTPS con autenticación.

### Error: "Updates were rejected"
Solución: Si el repositorio en GitHub ya tiene contenido, usa:
```bash
git pull origin main --allow-unrelated-histories
git push origin main
```

### Archivos que no deberían subirse
Asegúrate de que estos archivos NO estén en el commit:
- `.env` (archivos con secrets)
- `__pycache__/`
- `node_modules/`
- `.venv/`
- `db.sqlite3`

## Próximos Pasos

Una vez que el código esté en GitHub:

1. **Backend en Render:**
   - Ve a Render.com
   - Conecta tu cuenta de GitHub
   - Selecciona el repositorio
   - Configura según la guía en DESPLIEGUE.md

2. **Frontend en Vercel:**
   - Ve a Vercel.com
   - Conecta tu cuenta de GitHub
   - Selecciona el repositorio
   - Configura según la guía en DESPLIEGUE.md

## Comandos Útiles

```bash
# Ver estado de archivos
git status

# Ver historial de commits
git log --oneline

# Ver archivos en el último commit
git show --name-only

# Ver archivos que serán incluidos en el próximo commit
git diff --cached --name-only

# Si necesitas remover un archivo del commit
git reset HEAD archivo
```

## Autenticación con GitHub

Si es la primera vez que usas git con GitHub, necesitas configurar tu identidad:

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"
```

Para usar tokens de acceso personal (recommended):
1. Ve a GitHub Settings > Developer settings > Personal access tokens
2. Genera un nuevo token con permisos `repo`
3. Úsalo como contraseña cuando git te la pida
