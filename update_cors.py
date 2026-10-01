import os
from pathlib import Path

# Ruta al archivo .env
env_path = Path(__file__).parent / "barberia-backend" / ".env"

# Leer el archivo actual
if env_path.exists():
    with open(env_path, 'r') as f:
        content = f.read()

    # Actualizar CORS_ALLOWED_ORIGINS para incluir puerto 8082
    if "CORS_ALLOWED_ORIGINS" in content:
        # Reemplazar la línea de CORS
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('CORS_ALLOWED_ORIGINS='):
                # Agregar puerto 8082 si no está presente
                if '8082' not in line:
                    current_origins = line.split('=')[1]
                    new_origins = current_origins + ',http://localhost:8082,http://127.0.0.1:8082'
                    lines[i] = f'CORS_ALLOWED_ORIGINS={new_origins}'
                    print(f"Actualizado: {lines[i]}")
                break
        content = '\n'.join(lines)

    # Escribir el archivo actualizado
    with open(env_path, 'w') as f:
        f.write(content)

    print("Archivo .env actualizado correctamente para permitir puerto 8082")
else:
    print("Archivo .env no encontrado")
