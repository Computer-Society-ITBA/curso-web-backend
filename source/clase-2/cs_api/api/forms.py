# Importamos la clase de form para creación de usuario
from django.contrib.auth.forms import UserCreationForm
# Importamos el user de Django
from django.contrib.auth.models import User
# Importamos el error de validación
from django.forms import ValidationError
# Importamos nuestros modelos
from . import models

# Form para crear un usuario, tiene que extender a UserCreationForm esta form especial


class CreateUserForm(UserCreationForm):
    # En el meta ponemos que modelo usa
    # Y los campos que vamos a recibir,
    # deberían tener el mismo nombre que los campos del modelo
    # Password1 y Password2 son equivalentes a password y repeatPassword
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    # Este método se llama cuando se trata de validar el mail
    def clean_email(self):
        try:
            # Buscamos usuarios que tengan ese mail
            user = models.User.objects.get(
                email=self.cleaned_data.get('email'))
            # Si hay algún usuario, decimos que el mail ya está usado
            if user != None:
                raise ValidationError("Email ya en uso.")
            # Si está todo bien o no encuentra a un usuario,
            # devolvemos el email indicando que está ok
            return self.cleaned_data.get('email')
        except models.User.DoesNotExist:
            return self.cleaned_data.get('email')
