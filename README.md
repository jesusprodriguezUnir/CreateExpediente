# CreateExpediente

Pequeño repositorio para generar un diagrama y un documento Word que describen los flujos entre
GestorMapeos → ERP Académico → Expedientes.

Cómo usar

1. Instala dependencias:

```powershell
python -m pip install -r requirements.txt
```

2. Ejecuta el paquete:

```powershell
# Ejecutar como módulo
python -m CreateExpediente
# O ejecutar el script principal
python -c "from CreateExpediente import main; main()"
```

3. Salida:

Los ficheros generados se colocan en `CreateExpediente/output` (o en el directorio que indiques a `generate_diagram`).

Tests

```powershell
python -m unittest discover CreateExpediente/tests -v
```

Licencia: añade la tuya antes de subir al repositorio.
