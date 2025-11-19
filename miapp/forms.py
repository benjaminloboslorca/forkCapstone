# miapp/forms.py

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
# Eliminamos todas las importaciones que eran necesarias solo para el método save() sobrescrito.

# Obtiene el modelo de usuario (miapp.Cliente)
User = get_user_model() 

class CorreoPasswordResetForm(PasswordResetForm):
    """
    Formulario minimalista para la recuperación de contraseña.
    
    Solo se encarga de:
    1. Mostrar el campo de correo en el HTML.
    2. Usar la lógica de búsqueda correcta (campo 'correo').
    
    El proceso de generación de token y envío de correo lo maneja 
    la clase base PasswordResetForm, que ahora es compatible gracias 
    al alias 'email' en el modelo Cliente.
    """
    
    # 1. Definimos el campo que se mostrará al usuario (etiqueta en español)
    email = forms.EmailField(
        label=("Correo Electrónico"),
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'})
    )
    
    # 2. Sobrescribimos get_users para que la búsqueda use el campo 'correo'
    def get_users(self, email):
        """Dada una dirección de correo, retorna a los usuarios activos que coinciden."""
        # 🚨 LA ÚNICA LÓGICA NECESARIA 🚨
        active_users = User.objects.filter(correo__iexact=email, is_active=True)
        return active_users

    # El método save() no se define aquí; se hereda de PasswordResetForm.