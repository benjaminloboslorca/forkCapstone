import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tres_en_uno.settings')
django.setup()

from miapp.models import Cliente

# Datos del superusuario
EMAIL = 'ventas.tresenuno@gmail.com'
PASSWORD = 'Hortalizas2#' 
NOMBRE = 'Ventas'
TELEFONO = '942865185'

# Crear superusuario si no existe
if not Cliente.objects.filter(correo=EMAIL).exists():
    Cliente.objects.create_superuser(
        correo=EMAIL,
        nombre=NOMBRE,
        telefono=TELEFONO,
        password=PASSWORD
    )
    print(f"✅ Superusuario creado: {EMAIL}")
else:
    print(f"⚠️ El superusuario {EMAIL} ya existe")