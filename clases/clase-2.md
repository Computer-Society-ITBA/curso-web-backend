---
layout: default
title:  "Clase 2"
description: "Clase 2 - Usuarios, autenticación y permisos"
principal: false
active: true
---

# Clase 2

¡Bienvenidos a la clase número 2!

En esta clase vamos a ver como crear usuarios, como autenticarlos y como crear roles para los mismos.

Los temas de esta clase son:
- [Qué es la Autenticación](#qué-es-la-autenticación)
- [JWT Tokens](#jwt-tokens)
    * [Cómo se arma un JWT Token](#cómo-se-arma-un-jwt-token)
    * [Cómo funciona en nuestro caso](#cómo-funciona-en-nuestro-caso)
- [Modelos](#modelos)
- [Serializers vs Forms](#serializers-vs-forms)
- [Usuarios](#usuarios)
    * [Modelo default de Usuario](#modelo-default-de-usuario)
    * [Extendiendo al Usuario](#extendiendo-al-usuario)
    * [Endpoint para crear un usuario](#endpoint-para-crear-un-usuario)
        + [Form para crear el usuario](#form-para-crear-el-usuario)
        + [Serializer para el usuario](#serializer-para-el-usuario)
        + [Función en para crear el usuario](#función-en-para-crear-el-usuario)
        + [URL para crear un usuario](#url-para-crear-un-usuario)
    * [Probando la creación del usuario](#probando-la-creación-del-usuario)
    * [Endpoint para obtener usuarios](#endpoint-para-obtener-usuarios)
- [Autenticación](#autenticación)
    * [Log Out](#log-out)
- [Autorización](#autorización)
    * [Usando decorators](#usando-decorators)
    * [A mano](#a-mano)
    * [Probando la autorización](#probando-la-autorización)
- [Grupos y Permisos](#grupos-y-permisos)
    * [Cómo crear un grupo](#cómo-crear-un-grupo)
    * [Cómo asignar grupos](#cómo-asignar-grupos)
    * [Permisos hechos por nosotros](#permisos-hechos-por-nosotros)

***
***

## Setup

Vamos a partir de lo que estuvimos armando la clase anterior, así que en caso de que no hayas podido seguir la clase o tuviste problemas siguiéndola, [acá](bases/base-clase-2.zip) podés bajarte una copia del proyecto anterior (va a estar en un ZIP).

**NOTA**: Si nos pudiste seguir, no vamos a usar los endpoints de prueba que armamos, así que podes borrar las funciones de la view (`api/views.py`) y los URLs (`cs_api/urls.py`) y no tenés que hacer esta configuración.

Para poder configurarlo para estar listos vamos a seguir pasos similares a la clase anterior.

Extraer la carpeta del ZIP en donde vayan a dejar el proyecto, y muévanse dentro de la carpeta de *cs_api*.

**OPCIONAL**: Crear un virtualenv (en este caso usamos *virtualenv*), iniciarlo y chequear que la versión de Python sea 3.x (usamos 3.8.5 en el curso):
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

Corremos la API para ver que todo ande bien:
```bash
python manage.py runserver
```

***
***

## Qué es la Autenticación

Vamos a empezar diferenciando *Autenticación* y *Autorización*.

**Autenticación** --> Es el acto de validar que un usuario es quien dice ser, y si bien hay muchas formas de hacer esto, en nuestro caso vamos a estar autenticando a un usuario con un *nombre de usuario* + *contraseña*.

**Autorización** --> Es el proceso por el que un sistema (nuestra API) da permiso a un usuario de realizar una acción. Para que la API pueda determinar si tenemos permiso, tenemos que pasarle algo que indique que somos quien decimos ser, y que tenemos permisos.

En este caso, la forma de completar la autorización que vamos a usar es mediante **Tokens**. Una vez que nos autenticamos con la API, nos va a dar un *Token* que vamos a tener que usar en las requests que hagamos, para indicarle que somos nosotros y nos autorice a operar.

Este *Token* lo vamos a enviar en un header de la request de la siguiente manera: 
```bash
Authorization: JWT <TOKEN>
```

***

## JWT Tokens

Hay muchos diferentes tipos de *Tokens*, pero nosotros queremos que nuestra API sea realmente REST, por lo que vamos a usar **JWT Tokens** (*Jason Web Tokens*).

Estos *Tokens* son especiales porque permiten autorizar al usuario con solo el token y no hace falta guardar información del *Token* en la base de datos.

### Cómo se arma un JWT Token

Los [**JWT Tokens**](https://jwt.io/introduction) tienen 3 partes:
1. **Header** --> Generalmente consiste de 2 partes, el tipo de token (en este caso es `JWT`) y el algoritmo que se usa para firmarlo (`RSA` o `HMAC SHA256`). Ese JSON se codifica en **Base64Url** y es la primera parte:
    ```json
    {
      "alg": "HS256",
      "typ": "JWT"
    }
    ```
2. **Payload** --> Contiene las **Claims**, que son información respecto de una entidad, en este caso sería nuestro usuario. Hay 3 diferentes tipos de *Claims*, pero no nos vamos a concentrar en eso, lo importante es que hay ciertas *Claims* predefinidas, pero uno puede agregar más. Ese JSON se codifica en **Base64Url** y es la segunda parte:
    ```json
    {
      "sub": "1234567890",
      "name": "John Doe",
      "admin": true,
      "active": true
    }
    ```
3. **Signature** --> Esto es una firma del contenido del token, para firmar se agarra el header codificado, el payload codificado, un secreto y el algoritmo especificado antes, con eso se firma. Esta firma es para verificar que el contenido del token es válido, y que no fue cambiado en el medio.

Siempre van a tener esta forma: `xxxxx.yyyyy.zzzzz` (son más largos, pero tienen 3 partes separadas por `.`).

**IMPORTANTE**: Los tokens vencen, una vez que el token está vencido, no es más válido.

### Cómo funciona en nuestro caso

En nuestro caso, cuando hagamos un *login*, la API va a generar un JWT Token para el usuario y es lo que nos responde si el login fue exitoso.

Una vez que tenemos el token, cuando hagamos una request a la API, lo primero que va a hacer es ver si tenemos el token y verificar que el contenido es correcto, y después pasa a la función que hace lo que le pedimos a la API.

***

## Modelos

En Django nos vamos a referir a los objetos como *Modelos*. Cada modelo hace referencia a una tabla o relación dentro de la base de datos.

Django usa un **ORM**, [*Object–Relational Mapping*](https://en.wikipedia.org/wiki/Object%E2%80%93relational_mapping), que es una técnica de programación que abstrae a la base de datos de los modelos que usamos. Significa que vamos a poder hacer cosas como insertar en la base de datos sin necesidad de usar SQL, Django provee una gran variedad de métodos para interactuar con los modelos. Siempre nos vamos a referir a modelos, nunca a tablas ni nada similar.

La ventaja de usar el ORM es que podemos acceder a los objetos relacionados usando el operador `.`. Por ejemplo, si una transacción está asociada a un usuario, partiendo de una instancia del modelo `Transaction`, podemos obtener al usuario haciendo esto, `my_transaction.user`, y eso nos devuelve el modelo del usuario.

Estos modelos los declaramos dentro del archivo `api/models.py`.

***

## Serializers vs Forms

En Django existe lo que se llaman **Serializers** y **Forms**. En sí, ambos funcionan de manera muy similar, pero hay algunas diferencias.

Los [*Serializers*](https://www.django-rest-framework.org/api-guide/serializers/) están hechos más que nada para transformar a los modelos o datos en algo que sea fácilmente renderizable como un JSON o XML. Se les puede agregar validaciones también, y se pueden asociar a un modelo para acceder a campos especiales. Los declaramos en `api/serializers.py`.

Los [*Forms*](https://docs.djangoproject.com/en/3.1/topics/forms/) están hechos con el objetivo de escribir el form en Python y que luego se renderice como un HTML, pero no vamos a usar eso porque estamos armando una API REST. Se les puede agregar validaciones y asociar a modelos. Los declaramos en `api/forms.py`.

Nosotros vamos a usarlos de la siguiente manera, *Serializers* para devolver datos, y *Forms* para recibir datos. De esta forma, las validaciones solo son necesarias en los *Forms*, y los *Serializers* nos ocupamos de que sean la forma en la que nuestros modelos se representan al exterior.

**NOTA**: Los *Forms* solo se pueden usar para requests con GET y POST, así que en caso de tener un PUT vamos a usar un *Serializer* para recibir los datos.

***

## Usuarios

Django provee por default un modelo de usuario, que es el mismo que estuvimos usando para crear el superuser. Este modelo se puede extender, reemplazar o dejar intacto.

Para nuestro caso, como queremos que nuestros usuarios sean las `accounts` de la API, basta con extenderlo un poco. Simplemente queremos agregarle un campo que sea el *balance* de la cuenta.

Si quieren ver alternativas, la [documentación](https://docs.djangoproject.com/en/3.1/topics/auth/customizing/) de autenticación y usuarios explica como hacerlo.

### Modelo default de Usuario

Como mencionamos, Django tiene un modelo default de [usuario](https://docs.djangoproject.com/en/3.1/ref/contrib/auth/), el mismo tiene estos campos:
- **username** --> requerido
- **first_name** --> opcional
- **last_name** --> opcional
- **email** --> opcional
- **password** --> requerido
- **groups** --> roles del usuario
- **user_permissions** --> permisos del usuario
- **is_staff** --> determina si el usuario puede usar la consola de admin
- **is_active** --> determina si está activo el usuario, si no lo está, no puede loguearse
- **is_superuser** --> determina si es un superuser
- **last_login** --> última vez que el usuario se logueó
- **date_joined** --> fecha de creación

### Extendiendo al Usuario

Para extender al usuario vamos a empezar agregando nuestro modelo `Account` en `api/models.py`, que es lo que vamos a usar para extender al usuario (hay [alternativas](https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html) a como extender al usuario también):
```python
# Importamos a la clase "models" de Django
from django.db import models
# Importamos el modelo User default de Django
from django.contrib.auth.models import User

# Los modelos deben extender de models.Model
class Account(models.Model):
    # Definimos una relación 1a1 con el modelo de User para extenderlo
    # "on_delete=models.CASCADE" indica que si se borra el User, se borra el Account, y vice versa
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Campo "balance", es un campo de tipo "float", que no puede estar vacío ni nulo, y por default se pone en 0
    balance = models.FloatField(blank=False, null=False, default=0.0)
```

También vamos a registrar el modelo en el archivo `api/admin.py` para que podamos ver el modelo desde la consola de admin:
```python
from django.contrib import admin
# Importamos nuestros modelos
from api import models
# Registramos nuestro modelo
admin.site.register(models.Account)
```

Como agregamos un modelo hay que hacer las migraciones de nuevo:
```bash
python manage.py makemigrations && python manage.py migrate
```

Si corremos la API (`python manage.py runserver`), debería funcionar todo como antes, no deberíamos ver cambios.

### Endpoint para crear un usuario

Para poder armar un endpoint para crear un usuario necesitamos 4 cosas:
1. Un form dentro de `api/forms.py`
2. Un serializer para devolver lo que creamos dentro de `api/serializers.py`
3. Una función dentro de `api/views.py`
4. Agregar la función con una URL dentro de `cs_api/urls.py`

#### Form para crear el usuario

El form lo vamos a agregar en `api/forms.py` (si no existe el archivo, lo creamos), y va a tener lo siguiente:
```python
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
```

Como hereda de `UserCreationForm`, las validaciones de los campos las hace solas, y utiliza las validaciones default. 

Por cada campo que se define en `Meta`, existe una función que se puede definir que se llama `clean_CAMPO`, y se ejecuta después de validar al campo en sí. En este momento podemos definir nuestras propias validaciones también, como en este caso, que agregamos una validación para que no se puedan repetir los mails de los usuarios. Si encontramos algo que no nos gusta, hacemos un `raise ValidationError("Email ya en uso.")` para lanzar la excepción.

#### Serializer para el usuario

Vamos a definir un simple serializer para poder devolver al usuario que acabamos de crear. Lo definimos en `api/serializers.py` (si no existe el archivo lo creamos):
```python
from rest_framework import serializers
from django.contrib.auth.models import User

# Definimos un serializer que hereda de "ModelSerializer"
class UserSerializer(serializers.ModelSerializer):
    # En Meta ponemos que el modelo es el usuario
    # Ponemos que solo queremos esos 4 campos
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'is_active')
```

Este serializer sirve para devolver el usuario que acabamos de crear, simplemente estamos especificando que queremos que devuelva esos 4 campos (el último campo es para ver si está activo o no el usuario).

#### Función en para crear el usuario

Dentro de `api/views.py` vamos a crear nuestra función que se ocupa de recibir la request:
```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
# Importamos nuestros forms y modelos
from api import forms, models, serializers

# Definimos a la función con un POST
@api_view(['POST'])
def create_account(request):
    # Para usar las forms le pasamos el objeto "request.POST" porque esperamos que sea
    # un form que fue lanzado con un POST
    form = forms.CreateUserForm(request.POST)
    # Vemos si es válido, que acá verifica que el mail no exista ya
    if form.is_valid():
        # Guardamos el usuario que el form quiere crear, el .save() devuelve al usuario creado
        user = form.save()
        # Creamos la Account que va con el usuario, y le pasamos el usuario que acabamos de crear
        models.Account.objects.create(user=user)
        # Respondemos con los datos del serializer, le pasamos nuestro user y le decimos que es uno solo, y depués nos quedamos con la "data" del serializer
        return Response(serializers.UserSerializer(user, many=False).data, status=status.HTTP_201_CREATED)
    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
```

Es importante notar que como usamos un form, los datos tienen que venir en formato `x-www-form-urlencoded`, que significa que la request viene con un formato especial. Además llamamos al método `is_valid()` del form para que valide nuestros datos, si no lo llamamos nunca los valida. En caso de un error respondemos con los errores y un 400, y sino respondemos con los datos creados.

#### URL para crear un usuario

Para agregar la URL es muy simple, simplemente agregamos una entrada a la lista en `cs_api/urls.py`:
```python
urlpatterns = [
    ...,
    path('api/accounts', views.create_account, name="create_account")
]
```

### Probando la creación del usuario

Volvemos a correr la API (`python manage.py runserver`), y para probar crear usuarios vamos a usar **Curl**, para poder hacer un POST que vaya con el formato de los datos que queremos lo podemos hacer de esta manera:
```bash
curl -X POST -F 'username=gonzaloo' -F 'email=hirschgonzalo+gonzaloo@gmail.com' -F 'password1=Admin123!' -F 'password2=Admin123!' http://localhost:8000/api/accounts
curl -X POST -F 'username=testuser' -F 'email=hirschgonzalo+testuser@gmail.com' -F 'password1=Admin123!' -F 'password2=Admin123!' http://localhost:8000/api/accounts
```

Cada parámetro de nuestro form va con `-F NOMBRE=VALOR` y agregamos `-X POST` adelante de la request. Podemos ver que la API responde con lo que definimos en el serializer.

Y si probamos con un usuario repetido o generamos algún otro error, responde con un error:
```bash
curl -X POST -F 'username=testuser2' -F 'email=hirschgonzalo+testuser2@gmail.com' -F 'password1=Admin123!' -F 'password2=Admin123456!' http://localhost:8000/api/accounts
```

### Endpoint para obtener usuarios

Ahora que podemos crear usuarios, vamos a hacer un pequeño endpoint para obtenerlos. Dado que ya tenemos un serializer, no hace falta que armemos otro, podemos usar ese.

Hay que cambiar un poco nuestro código para crear un usuario porque queremos que se pueda usar la URL `/api/accounts` con un GET y un POST, pero cuando registramos la URL no podemos definir el método ahí. Entonces tenemos que cambiar un poco para que pueda tomar el caso GET y el caso POST.

En `api/views.py` cambiamos el código de esta forma y agregamos una función para listar usuarios:
```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
# Importamos nuestros forms y modelos
from api import forms, models, serializers

# Esta función es la que registramos en los urls
@api_view(['POST', 'GET'])
def accounts_view(request):
    # Hacemos el caso de un GET y el caso de un POST
    if request.method == 'GET':
        return get_accounts(request)
    else:
        return create_account(request)

def create_account(request):
    # Para usar las forms le pasamos el objeto "request.POST" porque esperamos que sea
    # un form que fue lanzado con un POST
    form = forms.CreateUserForm(request.POST)
    # Vemos si es válido, que acá verifica que el mail no exista ya
    if form.is_valid():
        # Guardamos el usuario que el form quiere crear, el .save() devuelve al usuario creado
        user = form.save()
        # Creamos la Account que va con el usuario, y le pasamos el usuario que acabamos de crear
        models.Account.objects.create(user=user)
        # Respondemos con los datos del serializer, le pasamos nuestro user y le decimos que es uno solo, y depués nos quedamos con la "data" del serializer
        return Response(serializers.UserSerializer(user, many=False).data, status=status.HTTP_201_CREATED)
    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

def get_accounts(request):
    # Obtenemos todos los usuarios y los serializamos
    users = serializers.UserSerializer(models.User.objects.all(), many=True).data
    # Agregamos los datos a la respuesta
    return Response(users, status=status.HTTP_200_OK)
```

Y en `cs_api/urls.py` cambiamos lo que estaba registrado en `api/accounts` para que sea así:
```python
path('api/accounts', views.accounts_view, name="accounts_view")
```

Volvemos a correr la API (`python manage.py runserver`) y podemos probar el endpoint de esta manera:
```bash
curl http://localhost:8000/api/accounts
```

***

## Autenticación

Como mencionamos antes, vamos a usar **JWT Tokens** para autenticar y autorizar a los usuarios.

Vamos a instalar un paquete de Django que simplifica todo esto:
```bash
pip install djangorestframework-jwt
```

Una vez instalado vamos a `cs_api/settings.py` y agregamos lo siguiente:
```python
# REST CONFIG
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}
```
Esto aclara en la configuración que usamos JWT para autenticar a nuestros usuarios.

Ahora hay que agregar 2 URLs especiales en `cs_api/urls.py`:
```python
# Importamos una view especial
from rest_framework_jwt.views import obtain_jwt_token
...
urlpatterns = [
    ...,
    path('api/auth/login', obtain_jwt_token),
]
```

Para probar este endpoint podemos usar un curl de esta manera:
```bash
curl -X POST -d 'username=testuser&password=Admin123!' http://localhost:8000/api/auth/login
```
**NOTA**: Tiene parámetros diferentes al curl para crear un usuario, esto es porque los datos del curl de login van a ir por body, mientras que los otros van en formato `x-www-form-urlencoded`.

Es importante notar que se puede configurar con mucha granularidad como funciona la autenticación, y hasta extenderla, pero nosotros nos quedamos con lo que viene de una por simpleza. Pero se puede encontrar más información en la [documentación](https://jpadilla.github.io/django-rest-framework-jwt/).

**NOTA 2**: Nos salteamos la opción de implementar que se puedan refrescar los tokens, no nos vamos a concentrar en eso porque no es tan importante para nuestro uso. Es muy fácil de implementar igual, es extremadamente similar al endpoint de login.

### Log Out

Podrán ver que no implementamos un *Log Out*, ¿por qué es eso?

Como la API es REST, no guardamos información de los tokens en el servidor, entonces no hay que borrar nada cuando uno quiere dejar de usar la API. Tampoco es necesario invalidar los JWT porque expiran en poco tiempo (en este caso 300 segundos, osea, 5 minutos), y tampoco tendríamos los medios para invalidarlo.

Simplemente si uno quiere hacer un *Log Out* y dejar de usar la API, solo basta con borrar el token de su computadora y listo.

***

## Autorización

Ahora ya tenemos **Autenticación**, pero nos hace falta definir **Autorización**, sin eso no sirven nuestros tokens.

Hay varias formas de definir los diferentes permisos y niveles de autorización en los endpoints. Si no definimos nada, por default están protegidos, entonces ahora no podemos crear usuarios porque por default está protegido el endpoint para crear usuarios. Necesitaríamos estar logueados para crear un usuario, y no es muy práctico.

Hay varias formas de definir permisos, pero nos vamos a concentrar en 2:
1. Usando decorators como `@permission_classes` y diferentes permisos --> Mucho más simple, pero hay casos en que no funciona
2. Ver permisos a mano --> Más repetitiva, pero sirve para algunos casos

### Usando decorators

Se puede importar un decorator, `@permission_classes` y ciertas clases de permisos que se especifican con operaciones como `|` y `&`, pero solo se pueden usar en funciones que tengan también el decorator `@api_view`. Esto ocurre porque estamos usando el enfoque funcional de las *Views*, si usaramos el enfoque por clases podríamos obviar la parte de hacerlo a mano también.

En casos como el que tenemos, cuando hay 2 métodos (GET y POST en este caso) en la misma función que tiene el `@api_view`, hay que combinar los decorators con ver a mano.

Para usar los decorators vamos a `api/views.py` y agregamos lo siguiente:
```python
# Importamos el decorator
from rest_framework.decorators import api_view, permission_classes
# Importamos los permisos
from rest_framework.permissions import AllowAny, IsAuthenticated
...
# Cambiamos accounts_view para agregarle el decorator
@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def accounts_view(request):
```

Acá lo que estamos haciendo es decir que para usar la URL `api/accounts`, independientemente del método, no hace falta estar autenticado, por eso `AllowAny`. Si quisieramos que cualquiera autenticado pudiera usarlo, usaríamos `IsAuthenticated`.

En nuestro caso queremos que para crear un usuario no haga falta estar logueado, pero cuando querés listar a los usuarios si es necesario, por eso le damos el permiso más abarcativo, que lo usen todos. Necesitamos un poco a mano ahora.

También se puede definir los propios permisos, pero eso más adelante.

### A mano

Para poder ver a mano los permisos, usamos la `request` que todas las funciones que declaramos reciben. Este objeto `request` tiene a un `User` relacionado, por lo que podemos ver que user está logueado en la `request` (si no hay ningún usuario logueado, el usuario es un `AnonymousUser`).

Dentro de nuestra función de obtener usuarios podemos ver si el usuario está logueado o no, y devolver una respuesta acorde. En `api/views.py` agregamos:
```python
def get_accounts(request):
    # Chequear que no sea anónimo <-- AGREGAMOS ESTO
    # Si no está autenticado, devolvemos un 401
    if not request.user.is_authenticated():
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    # Obtenemos todos los usuarios y los serializamos
    users = serializers.UserSerializer(models.User.objects.all(), many=True).data
    # Agregamos los datos a la respuesta
    return Response(users, status=status.HTTP_200_OK)
```

**NOTA**: Dependiendo de la versión de Django la parte `request.user.is_authenticated()` puede ser un atributo y se usa así `request.user.is_authenticated`.

### Probando la autorización

Una vez que mezclamos las 2 formas de manejar la autorización, podemos hacer pruebas.

Probamos lo siguiente:
1. Crear un usuario --> Hacer como en secciones anteriores
2. Loguearse --> Hacer como en secciones anteriores
3. Obtener usuarios
  - Si ponemos un token de esta forma nos da OK:
  ```bash
  curl -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjozLCJ1c2VybmFtZSI6InRlc3R1c2VyIiwiZXhwIjoxNjEyMDQ5NDIyLCJlbWFpbCI6ImhpcnNjaGdvbnphbG8rdGVzdHVzZXJAZ21haWwuY29tIn0.FrQ1bN3x-onD_pPW4w20GriYFKA3r9ERsD6N6UTyiOg" http://localhost:8000/api/accounts
  ```
  - Si no ponemos un token, nos da un 401 y no devuelve nada:
  ```bash
  curl http://localhost:8000/api/accounts
  ```

¡Ya tenemos autorización! :)

***

## Grupos y Permisos

Un **permiso** es una autorización para realizar una acción que podemos darle a los usuarios (no nos vamos a concentrar en esto).

Un **grupo** es una forma de categorizar usuarios y de esa forma darles permisos.

Los *grupos* (o roles) nos sirven para definir acciones que nuestros distintos tipos de usuarios pueden realizar. En nuestro caso vamos a tener 2 grupos, `user` y `admin`. En el caso de nuestra API bancaria no hay mucha diferencia entre las acciones que puede hacer un admin y un usuario. La diferencia es que el `admin` va a poder borrar usuarios y cambiarles el grupo a los usuarios.

### Cómo crear un grupo

No vamos a necesitar un endpoint para esto porque queremos crearlos una sola vez a los grupos. Tenemos 2 opciones:
1. Crearlos a mano desde la consola de admin --> Si queremos llevar nuestro código a otro lado sin la base, tenemos que volver a hacerlo, y es poco práctico
2. Armar un pequeño código que los cree solos

Crear un grupo es tan fácil como crear un usuario, pero antes queremos definir los nombres en algún lugar, en el archivo `api/constants.py` (si no existe lo creamos) vamos a definir nuestras constantes de ahora en más:
```python
GROUP_USER = "user"
GROUP_ADMIN = "admin"
```

Y ahora en el archivo `api/admin.py` vamos a agregar un par de líneas que se ocupan de crear a los grupos:
```python
# Importamos nuestros modelos
from api import models, constants
# Importamos el modelo de Group
from django.contrib.auth.models import Group
# Importamos el error que no se pudo hacer la operación
from django.db.utils import OperationalError
...
# Creamos el grupo de ADMIN
try:
	group, created = Group.objects.get_or_create(name=constants.GROUP_ADMIN)
	if created:
	    print("Admin creado exitosamente")
	else:
	    print("Admin ya existía, no fue creado")
	# Creamos el grupo de USER
	group, created = Group.objects.get_or_create(name=constants.GROUP_USER)
	if created:
	    print("User creado exitosamente")
	else:
	    print("User ya existía, no fue creado")
except OperationalError:
	print("No existe la base de datos de los grupos")
```

El código lo que hace es usar el método `get_or_create` de los modelos, de forma que si ya existe el grupo no lo crea, y además imprimimos un pequeño mensaje en la consola donde corre Django para indicar si lo creamos o no. Este código se corre cuando se levanta la API, entonces nos aseguramos de que siempre existan los grupos.

**NOTA**: Usamos un *try-catch* con un *OperationalError* para evitar problemas al hacer las migraciones si clonamos el proyecto. Como antes de hacer las migraciones no hay tablas, puede generar una excepción, pero con esto lo evitamos

### Cómo asignar grupos

Ahora tenemos nuestros grupos, pero no se los asignamos a nuestros usuarios, entonces hay que cambiar eso.

Tenemos que cambiar nuestro código para crear usuarios, para que ahora le agregue el grupo cuando lo crea. En el archivo `api/views.py` agregamos un par de líneas que se ocupan de eso, de forma que nuestra función `create_account` queda así:
```python
# Agregamos "constants" a lo que importamos
from api import forms, models, serializers, constants
# Importamos la clase Group
from django.contrib.auth.models import Group

def create_account(request):
    # Para usar las forms le pasamos el objeto "request.POST" porque esperamos que sea
    # un form que fue lanzado con un POST
    form = forms.CreateUserForm(request.POST)
    # Vemos si es válido, que acá verifica que el mail no exista ya
    if form.is_valid():
        # Guardamos el usuario que el form quiere crear, el .save() devuelve al usuario creado
        user = form.save()
        # Agregamos por default el grupo user a todos los usuarios
        # IMPORTANTE --> AGREGAMOS SOLO ESTA LINEA!
        user.groups.add(Group.objects.get(name=constants.GROUP_USER))
        # Creamos la Account que va con el usuario, y le pasamos el usuario que acabamos de crear
        models.Account.objects.create(user=user)
        # Respondemos con los datos del serializer, le pasamos nuestro user y le decimos que es uno solo, y depués nos quedamos con la "data" del serializer
        return Response(serializers.UserSerializer(user, many=False).data, status=status.HTTP_201_CREATED)
    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
```

Ahora cada vez que creamos un usuario, se va a crear como un `user`.

Seguimos teniendo un pequeño problema igual, nuestro superuser no tiene el rol de `admin`, y los usuarios que creamos antes tampoco tienen su rol de `user`. Para corregir esto tenemos que entrar a la consola de admin, ir a cada usuario que no tenga grupo y agregarle el grupo correspondiente (o borrar los usuarios, excepto el superuser). Los grupos se agregan acá:
![Django admin roles](resources/clase-1/django_admin_roles.png "Django admin roles")
Después de poner al grupo en la parte derecha, hay que guardar los cambios.

### Permisos hechos por nosotros

Ya que tenemos grupos, ahora podemos definir nuestros propios permisos, y vamos a probar crear estos permisos para armar un endpoint para borrar a un usuario, pero que solo un admin pueda hacer esto. Este endpoint va a estar en `api/accounts/<id>` con un DELETE.

Vamos a empezar armando nuestro propio permiso, en el archivo `api/permissions.py` (si no existe lo creamos), vamos a definir nuestro propio permiso `IsAdmin`:
```python
from api import constants, models
from rest_framework.permissions import BasePermission

# La clase IsAdmin es nuestro permiso, que tiene que extender de BasePermission para que sea un permiso
class IsAdmin(BasePermission):
    # Mensaje de error que va a devolver
    message = "El usuario no es admin"

    # La función has_permission devuelve True si tiene permiso o False si no lo tiene
    # request.user es el usuario que está autenticado y manda el token
    def has_permission(self, request, view):
        # Si no tiene grupos le decimos que no de una
        if not request.user.groups.exists():
            return False
        # Asumimos en este caso que cada usuario va a tener 1 solo grupo, aunque puede tener más
        # Este código funciona solo si tiene 1 grupo, si tiene más habria que definir una política para
        # ver si el usuario tiene permiso al tener más de 1 grupo
        # Devuelve True si es admin, False si no lo es
        return request.user.groups.all()[0].name == constants.GROUP_ADMIN
```

Una vez que tenemos nuestro permiso creado, vamos a `api/views.py` para crear el endpoint:
```python
# Importamos nuestro permiso
from api.permissions import IsAdmin

# Especificamos un DELETE
@api_view(['DELETE'])
@permission_classes([IsAdmin])  # Definimos que tiene que ser un admin
def user_delete(request, id):
    # No dejamos que un usuario se borre a si mismo
    # Vemos si el ID del usuario de la request es igual al que se manda en la URL
    if request.user.id == id:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    # Necesitamos un try-catch porque tal vez el usuario no existe
    try:
        # Buscamos al usuario por ID
        user = models.User.objects.get(pk=id)
        # Borramos al usuario
        user.delete()
        # Devolvemos que no hay contenido porque lo pudimos borrar
        return Response(status=status.HTTP_204_NO_CONTENT)
    except models.User.DoesNotExist:
        # Si no existe le damos un 404
        return Response(status=status.HTTP_404_NOT_FOUND)
```

Es importante ver que como esperamos que el endpoint esté en `api/accounts/<id>` el parámetro `id` se lo pasamos a la función.

Ahora queda registrar la URL en `cs_api/urls.py` y listo (noten que especificamos que es un `int`):
```python
urlpatterns = [
    ...,
    path('api/accounts/<int:id>', views.user_delete, name="user_delete"),
    ...
]
```

Ahora podemos volver a correr la API (`python manage.py runserver`) y teniendo el token de un admin, borrar a un usuario:
```bash
# Con token de admin
curl -X DELETE -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6ImdvbnphbG8iLCJleHAiOjE2MTIxMDgwNDIsImVtYWlsIjoiZ2hpcnNjaEBpdGJhLmVkdS5hciJ9.uNRkEJ1jnzKU6l5dXA2bc4Z5sXJ4DhuQ1fDQNhI-xIU" http://localhost:8000/api/accounts/1
```

Y si no le damos un token, le damos el token de un `user` o le damos un ID que no existe, tira error:
```bash
# Sin token
curl -X DELETE http://localhost:8000/api/accounts/1
# Con token de user
curl -X DELETE -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjozLCJ1c2VybmFtZSI6InRlc3R1c2VyIiwiZXhwIjoxNjEyMTA4MTg2LCJlbWFpbCI6ImhpcnNjaGdvbnphbG8rdGVzdHVzZXJAZ21haWwuY29tIn0.HEAunNAdY2c95uwR3iLDQcAWFAmrj1zDz1TTdVNeh-U" http://localhost:8000/api/accounts/1
# Con id que no existe
curl -X DELETE -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6ImdvbnphbG8iLCJleHAiOjE2MTIxMDgwNDIsImVtYWlsIjoiZ2hpcnNjaEBpdGJhLmVkdS5hciJ9.uNRkEJ1jnzKU6l5dXA2bc4Z5sXJ4DhuQ1fDQNhI-xIU" http://localhost:8000/api/accounts/1000
# Con id del mismo usuario, borrarse a si mismo, en mi caso mi id es 2
curl -X DELETE -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6ImdvbnphbG8iLCJleHAiOjE2MTIxMDgwNDIsImVtYWlsIjoiZ2hpcnNjaEBpdGJhLmVkdS5hciJ9.uNRkEJ1jnzKU6l5dXA2bc4Z5sXJ4DhuQ1fDQNhI-xIU" http://localhost:8000/api/accounts/2
```

***

Eso es todo por esta clase, pueden seguir con la [clase 3](clase-3.md)
