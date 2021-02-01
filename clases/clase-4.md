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

Ahora nos enfocamos en el perfil del usuario, vamos a usar un endpoint que sea `api/accounts/<id>` con un GET.

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

Nos falta un solo endpoint ahora, uno para poder agregar fondos a nuestra cuenta. Para hacer esto vamos a usar un endpoint `api/accounts/<id>` con PUT.

Vamos a definir 2 comportamientos para el endpoint, los usuarios solo pueden agregar a su balance, mientras que el admin puede agregar balance y cambiar el rol del usuario.

### Serializer

Ya tenemos un serializer (el que creamos antes), pero necesitamos agregarle una validación para que el balance no pueda ser menor que el actual, en `api/serializers.py` agregamos el siguiente método en `UserDetailsSerializer`:
```python
# Agregamos el "validate" para ver que no estén tratando de sacar balance
def validate(self, data):
    # Usamos un context, que es algo que se le puede pasar al serializer al momento de instanciarlo
    if data['balance'] < self.context['user'].account.balance:
        raise serializers.ValidationError(
            "Invalid balance, cannot be less than current")
    return data
```

Ya tenemos la validación en el `GroupSerializer`, así que no hace falta agregarla.

### View Funcional

Ahora hay que agregar el caso PUT en `api/views.py`, teniendo en cuenta que dependiendo del grupo del usuario, va a poder hacer cosas diferentes:
```python
# Agregamos el caso en la función registrada
@api_view(['DELETE', 'GET', 'PUT'])
@permission_classes([IsOwner | IsAdmin])
def user_specific_view(request, id):
    # Hacemos el caso de un GET y el caso de un DELETE
    if request.method == 'GET':
        return get_user(request, id)
    elif request.method == 'PUT':
        return user_update(request, id)
    else:
        return user_delete(request, id)

def user_update(request, id):
    # Necesitamos un try-catch porque tal vez el usuario no existe
    try:
        # Buscamos al usuario por ID
        user = models.User.objects.get(pk=id)
        # Creamos el serializer, con el context como el user
        serializer = serializers.UserDetailsSerializer(data=request.data, context={'user': user})
        # Vemos que sea válido, sinó damos error
        if serializer.is_valid():
            # En caso que sea el usuario, permitimos el cambio de balance
            if request.user.groups.all()[0].name == constants.GROUP_USER:
                # Cambiamos balance, accedemos así porque como usamos un "source" en el campo
                # Al recibirlo lo toma en la jerarquía del "source" que habíamos definido
                user.account.balance = serializer.validated_data.get('account')['balance']
                # Guardamos
                user.account.save()
            else:
                # Vemos que no se saque el rol a sí mismo
                if id == request.user.id and serializer.groups[0].name != constants.GROUP_ADMIN:
                    return Response({"Error": "No se puede cambiar el propio rol"}, status=status.HTTP_400_BAD_REQUEST)
                # Recuperamos el nuevo rol, accedemos así porque el objeto es un OrderedDic
                group = Group.objects.get(name=serializer.validated_data.get('groups')[0].get('name'))
                # Cambiamos balance, accedemos así porque como usamos un "source" en el campo
                # Al recibirlo lo toma en la jerarquía del "source" que habíamos definido
                user.account.balance = serializer.validated_data.get('account')['balance']
                # Sacamos roles actuales
                user.groups.clear()
                # Agregamos el nuevo rol
                user.groups.add(group)
                # Guardamos
                user.account.save()
                user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except models.User.DoesNotExist:
        # Si no existe le damos un 404
        return Response(status=status.HTTP_404_NOT_FOUND)
```

Dependiendo del rol dejamos que haga algo diferente, pero esperamos recibir lo mismo que devolvemos en el GET.

### Probando el Endpoint

Para probar el endpoint simplemente hay que tener a un usuario logueado (está bueno probar con y sin admin) y ejecutar el siguiente curl (en mi caso el ID del usuario era 5):
```bash
curl -i -X PUT -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo1LCJ1c2VybmFtZSI6InRlc3R1c2VyMSIsImV4cCI6MTYxMjIyMzcwNCwiZW1haWwiOiJoaXJzY2hnb256YWxvK3Rlc3R1c2VyMUBnbWFpbC5jb20ifQ.aP2YwbjYy9TlK0i8g0MV-2oevsSOTped_cOclXFPhMw" -H "Content-Type: application/json" http://localhost:8000/api/accounts/5 -d '{"balance": 1000.0,"email": "hirschgonzalo+testuser1@gmail.com","groups": [{"name": "user"}],"id": 5,"username": "testuser1"}'
```

Se puede probar también cambiarle el rol a otro usuario (estando con un admin):
```bash
curl -i -X PUT -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImdvbnphbG8iLCJleHAiOjE2MTIyMjM4NTUsImVtYWlsIjoiZ2hpcnNjaEBpdGJhLmVkdS5hciJ9.nod24byOncyvPmefG5ZGktjugaK9qAoMMFfNPCgl4Ic" -H "Content-Type: application/json" http://localhost:8000/api/accounts/6 -d '{"id":6,"email":"hirschgonzalo+testuser2@gmail.com","username":"testuser2","groups":[{"name":"admin"}],"balance":100.0}'
```