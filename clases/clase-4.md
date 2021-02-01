---
layout: default
title:  "Clase 4"
description: "Clase 4 - Acciones del usuario, mailing y un caso real"
principal: false
---

# Clase 4

¡Bienvenidos a la clase número 4!

En esta clase vamos a ver como armar acciones para el usuario, envío de mails y un caso real de API en Django.

Los temas de esta clase son:
TODO TEMAs

***
***

## Setup

Vamos a partir de lo que estuvimos armando la clase anterior, así que en caso de que no hayas podido seguir la clase o tuviste problemas siguiendola, [aca](bases/base-clase-4.zip) podés bajarte una copia del proyecto anterior (va a estar en un ZIP).

**NOTA**: Si nos pudiste seguir y pudiste hacer los ejercicios no hace falta esto (si no pudiste hacer los ejercicios no hay problema, en el ZIP están resueltos).

Para poder configurarlo para estar listos vamos a seguir pasos similares a la clase anterior.

Extraer la carpeta del ZIP en donde vayan a dejar el proyecto, y muevanse dentro de la carpeta de *cs_api*.

**OPCIONAL**: Crear un virtualenv (en este caso usamos *virtualenv*), iniciarlo y checkear que la versión de Python sea 3.x (usamos 3.8.5 en el curso):
```bash
virtualenv ./cs_env
source ./cs_env/bin/activate
python --version
```

Desde la carpeta de *cs_api*, vamos a instalar los paquetes de la clase pasada:
```bash
pip install -r requirements.txt
```

Hacemos las migraciones:
```bash
python manage.py makemigrations && python manage.py migrate
```

Creamos el superuser de nuevo (acordate de hacerlo un admin):
```bash
python manage.py createsuperuser
```

Corremos la api para ver que todo ande bien:
```bash
python manage.py runserver
```

***
***

## Perfil del Usuario

A nuestra API le falta un poco de trabajo todavía, nos faltan 2 endpoints. Necesitamos un endpoint para poder obtener el propio perfil, y un endpoint para poder alterar el balance.

Ahora nos enfocamos en el perfil del usuario.

### Serializers

Antes de empezar a armar un endpoint nuevo hay que pensar que vamos a necesitar un nuevo serializer, necesitamos poder enviar y recibir información del usuario. Queremos devolver `id`, `username`, `email`, `balance` y `grupos`. Este nuevo serializer lo hacemos separado del que ya tenemos porque queremos mostrar información extra y sensible, como el balance por ejemplo.

Vamos a armar unos serializers que nos permitan eso (en `api/serializers.py`):
```python
from api import models, constants

class GroupSerializer(serializers.Serializer):
    # Definimos que solo tiene el nombre
    name = serializers.CharField(required=True)
    # Definimos la validación
    def validate(self, data):
        if data['name'] not in [constants.GROUP_ADMIN, constants.GROUP_USER]:
            raise serializers.ValidationError(
                "Grupo Inválido")
        return data

class UserDetailsSerializer(serializers.ModelSerializer):
    # Definimos los grupos con un serializer más para controlar la representación
    groups = GroupSerializer(many=True)
    # Definimos campos como read_only 
    id = serializers.IntegerField(read_only=True)
    email = serializers.CharField(read_only=True)
    username = serializers.CharField(read_only=True)
    # Definimos balance como un method field porque está asociado a la Account del user
    balance = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'groups', 'balance')

    # Cuando se define un SerializerMethodField hay que crear un método que sea "get_CAMPO"
    # donde CAMPO es el nombre del campo que definimos
    def get_balance(self, obj):
        return obj.account.balance
```

Definimos algunos campos como read_only para que no intente crearlos el serializer, y usamos un `GroupSerializer` para tener control de la información que muestra de los grupos.

### Permisos

Vamos a necesitar definir un permiso más, queremos que el endpoint de editar el balance lo pueda usar solo el admin y el user que es "dueño" del perfil. 

Vamos a definir el permiso `IsOwner` en `api/permissions.py`:
```python
# La clase IsOwner es nuestro permiso
class IsOwner(BasePermission):
    message = "No es el dueño del perfil"

    def has_permission(self, request, view):
        # Vemos si viene el ID dentro de los parámetros
        if 'id' in view.kwargs:
            try:
                # Recuperamos el user basado en lo que viene en la request
                user = models.User.objects.get(pk=view.kwargs['id'])
                # Vemos que sea el mismo user que hizo la request
                return request.user == user
            except models.User.DoesNotExist:
                return False
            return False
        return False
```
Vemos que coincida el usuario al que está dirigida la request y el usuario que envió la request.

**NOTA**: Este permiso solo sirve en los endpoints que son `api/accounts/<id>` ya que asume que el ID del que se habla es de un usuario y no de una transacción por ejemplo.

### View Funcional

Ahora tenemos que armar la view que se encarga de devolvernos el usuario que queremos. Ya teníamos una view registrada para el url `api/accounts/<id>` con un DELETE, así que vamos a tener que adaptar nuestro código en `api/views.py`:
```python
@api_view(['DELETE', 'GET'])
@permission_classes([IsOwner | IsAdmin])
def user_specific_view(request, id):
    # Hacemos el caso de un GET y el caso de un DELETE
    if request.method == 'GET':
        return get_user(request, id)
    else:
        return user_delete(request, id)

def get_user(request, id):
    # Necesitamos un try-catch porque tal vez el usuario no existe
    try:
        # Buscamos al usuario por ID
        user = models.User.objects.get(pk=id)
        # Serializamos al user
        return Response(serializers.UserDetailsSerializer(user, many=False).data, status=status.HTTP_200_OK)
    except models.User.DoesNotExist:
        # Si no existe le damos un 404
        return Response(status=status.HTTP_404_NOT_FOUND)

def user_delete(request, id):
    # No dejamos que un usuario se borre a si mismo
    # Vemos si el ID del usuario de la request es igual al que se manda en la URL
    # Vemos de asegurarnos que sea un admin
    if request.user.id == id:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    elif request.user.groups.all()[0].name != constants.GROUP_ADMIN:
        return Response(status=status.HTTP_403_FORBIDDEN)

    # Necesitamos un try-catch porque tal vez el usuario no existe
    try:
        # Buscamos al usuario por ID
        user = models.User.objects.get(pk=id)
        # Hacemos que no esté activo en vez de borrado físico
        user.is_active = False
        user.save()
        # Devolvemos que no hay contenido porque lo pudimos borrar
        return Response(status=status.HTTP_204_NO_CONTENT)
    except models.User.DoesNotExist:
        # Si no existe le damos un 404
        return Response(status=status.HTTP_404_NOT_FOUND)
```

Tuvimos que sacarle el `@api_view` y `@permission_classes` a `user_delete()` porque la función que vamos a registrar para la url es `user_specific_view`, y también agregamos en `user_delete()` que se fije que es un admin a mano.

A `user_specific_view` le pusimos que use `@permission_classes([IsOwner | IsAdmin])` para que pueda tener cualquiera de los 2 permisos basados en los roles.

Con la nueva función, hay que cambiar la url en `cs_api/urls.py` para que la use:
```python
urlpatterns = [
    ...,
    path('api/accounts/<int:id>', views.user_specific_view, name="user_specific_view"),
    ...
]
```

### Probando el endpoint

Para probar el endpoint simplemente hay que tener a un usuario logueado (y que no sea `admin`) y ejecutar el siguiente curl (en mi caso el ID del usuario era 5):
```bash
curl -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo1LCJ1c2VybmFtZSI6InRlc3R1c2VyMSIsImV4cCI6MTYxMjIxOTY2OSwiZW1haWwiOiJoaXJzY2hnb256YWxvK3Rlc3R1c2VyMUBnbWFpbC5jb20ifQ.aHc0LPCDKpzt50pnBUaoX01ZgQm7DIB474d05iYAhGI" http://localhost:8000/api/accounts/5
```

Podemos probar también ponerle otro ID de usuario para ver como falla:
```bash
curl -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo1LCJ1c2VybmFtZSI6InRlc3R1c2VyMSIsImV4cCI6MTYxMjIxOTY2OSwiZW1haWwiOiJoaXJzY2hnb256YWxvK3Rlc3R1c2VyMUBnbWFpbC5jb20ifQ.aHc0LPCDKpzt50pnBUaoX01ZgQm7DIB474d05iYAhGI" http://localhost:8000/api/accounts/6
```

***

## Agregar Fondos





