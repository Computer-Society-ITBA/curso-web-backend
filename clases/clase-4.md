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

Y con esto nuestra API ya está funcionando y tiene todo lo que queríamos.

***

## Mailing

Algo muy utilizado en las aplicaciones hoy en día es el envío de mails. Sirve como algo informativo para el usuario o para generar interés en la aplicación. Otro uso muy común es para poder verificar la cuenta de un usuario, para evitar que alguien cree y use muchos usuarios sin verificarlos.

### Cómo funciona

Para poder verificar a un usuario necesitamos alguna forma de darle un secreto que él solo nos pueda responder. Para hacer esto, cuando se crea un usuario vamos a generar un token especial que se guarda en la base de datos, y que al momento de hacer click en el link que le llega por mail, se verifica con la base si es válido o no.

### Configuración

Es relativamente simple configurar mailing en Django, lo primero que hay que hacer es agregar algunas configuraciones en `cs_api/settings.py`:
```python
import os
# Mailing
# De done sale el mail
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
MAILER_EMAIL_BACKEND = EMAIL_BACKEND
# Host del mail, gmail en este caso
EMAIL_HOST = 'smtp.gmail.com'
# Puerto de gmail
EMAIL_PORT = 587
# Indicamos que use TLS
EMAIL_USE_TLS = True
# Desactivamos SSL
EMAIL_USE_SSL = False
# Usuario
EMAIL_HOST_USER = 'restreview.toptal@gmail.com'
# Contraseña, usamos os.environ para evitar mostrarla, es más seguro
EMAIL_HOST_PASSWORD = os.environ.get('MAIL_PASS')
# Indicamos de donde sale el mail, es "NOMBRE<DIRECCION>"
DEFAULT_FROM_EMAIL = 'CSBankingAPI<restreview.toptal@gmail.com>'
# Asunto del mail
SUBJECT = 'Verificá tu Cuenta'
# De donde salen los templates
SETTINGS_PATH = os.path.normpath(os.path.dirname(__file__))
TEMPLATE_DIRS = (
    os.path.join(SETTINGS_PATH, 'templates'),
)
```

Noten que usamos `os.environ.get('MAIL_PASS')` para importar la contraseña del mail, esto hace que sea seguro porque no la estamos guardando en el código. Para poder hacer esto, en la terminal donde está corriendo el proyecto hay que hacer:
- Si tienen Linux/OSx (Mac):
    ```bash
    # Crear la variable
    export MAIL_PASS='TU_CONTRASEÑA'
    # Ver que se creó bien
    echo $MAIL_PASS
    ```
- Si tienen Windows pueden usar este [link](http://www.dowdandassociates.com/blog/content/howto-set-an-environment-variable-in-windows-command-line-and-registry/) para ver como hacerlo

### Templates

Como vamos a estar enviando emails, podemos usar templates para que los mails sean bonitos. Para hacer esto ya creamos unas templates que pueden bajarse [acá](bases/templates.zip). Ese ZIP tiene 2 archivos dentro de una carpeta `templates`, `emailVerify.html` e `emailVerify.txt`. El primero es la versión HTML de la template, y el segundo es la versión texto de la template, por si no se puede usar HTML. 

Esta carpeta `templates` debería estár adentro de la carpeta `api`.

### Envío de mails

Vamos a tener que armar algo para poder enviar nuestros mails, para eso vamos a crear un nuevo archivo (`api/mailing.py`) para poner toda nuestra lógica ahí:
```python
# Mailing
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.contrib.auth.tokens import default_token_generator

# Envía el email de confirmación
def send_confirmation_email(user, request):
    # Obtiene el link al sitio
    current_site = get_current_site(request)
    # Genera los templates
    plaintext = get_template('emailVerify.txt')
    html_template = get_template('emailVerify.html')
    # Le pasa los datos a cada template para que la customize
    data = {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),  # Genera el token
    }
    text_content = plaintext.render(data)
    html_content = html_template.render(data)
    # Seteamos asunto
    mail_subject = 'Verificá tu Cuenta'
    # Definimos el mail con contenido texto
    msg = EmailMultiAlternatives(mail_subject, text_content, to=[user.email])
    # Agregamos versión HTML
    msg.attach_alternative(html_content, "text/html")
    # Enviamos
    msg.send()
```

Este método se ocupa de llenar los templates con los datos del usuario y enviar el mail.

### Creación de usuario sin verificar

Hay que modificar nuestro código de creación de un usuario para poder agregar que empiece sin verificar, y que además le mande un mail cuando lo crea. Para esto vamos a `api/views.py` y agregamos esto:
```python
from api import forms, models, serializers, constants, pagination, extractor, mailing
def create_account(request):
    # Para usar las forms le pasamos el objeto "request.POST" porque esperamos que sea
    # un form que fue lanzado con un POST
    form = forms.CreateUserForm(request.POST)
    # Vemos si es válido, que acá verifica que el mail no exista ya
    if form.is_valid():
        # Guardamos el usuario que el form quiere crear, el .save() devuelve al usuario creado
        # Commit en false para que espere para guardarlo
        user = form.save(commit=False)
        # Marcamos como inactivo y guardamos
        user.is_active = False
        user.save()
        # Agregamos por default el grupo user a todos los usuarios
        user.groups.add(Group.objects.get(name=constants.GROUP_USER))
        # Creamos la Account que va con el usuario, y le pasamos el usuario que acabamos de crear
        models.Account.objects.create(user=user)
        # Una vez que guardamos todo, enviamos el mail
        mailing.send_confirmation_email(user, request)
        # Respondemos con los datos del serializer, le pasamos nuestro user y le decimos que es uno solo, y depués nos quedamos con la "data" del serializer
        return Response(serializers.UserSerializer(user, many=False).data, status=status.HTTP_201_CREATED)
    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
```

Alteramos nuestra función para crear un usuario para que cree a los usuarios inicialmente no verificados, y cuando crea todo les manda un mail.

### Cómo verificar la cuenta

Nos falta como verificar a nuestro usuario cuando tenemos el email. 

En el email viene un link que va a estar dirigido a una URL especial de nuestra API que se va a encargar de verificar a los usuarios. En `api/views.py` agregamos el método que va a verificarlos:
```python
# Mailing
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode

@api_view(['GET'])
@permission_classes([AllowAny])
def activate(request, uidb64, token):
    try:
        # Extraemos user id y recuperamos al usuario
        uid = urlsafe_base64_decode(uidb64).decode()
        user = models.User.objects.get(pk=uid)
        # Verificamos el token
        if user != None and default_token_generator.check_token(user, token):
            # Marcamos como activo
            user.is_active = True
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
    except models.User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    return Response(status=status.HTTP_400_BAD_REQUEST)
```

Y nos falta registrar la url en `cs_api/urls.py` para poder acceder a la función de recién:
```python
urlpatterns = [
    ...,
    path('api/auth/activate/<uidb64>/<token>/', views.activate, name='activate'),
]
```

La url tiene ese formato porque va a recibir como Path Param el id del usuario en base 64 y el token.

### Probamos la verificación

Ahora podemos crear nuevos usuarios (va a tardar un poco más el endpoint porque está enviando el mail), y pueden ver que cuando tratan de hacer un login sin verificar la cuenta no los deja.

Si crean un usuario nuevo deberían recibir un mail, y al hacer click en el botón les va a aparecer una pantalla fea que tiene un error. Eso es porque deberíamos definir en el endpoint de activación un *Redirect*, pero no tenemos a donde redirigir al usuario, y por ahora no nos importa. Si usaran curl con la url que tiene el botón con un GET, podrían ver que se puede y devuelve el status code apropiado.

Una ver verificada la cuenta pueden volver a tratar de hacer un login y van a ver que funciona.

Para usar un curl con el link del mail pueden hacer:
```bash
curl -i LINK_DEL_MAIL
```

***

## Caso Real

Vamos a ver como sería un caso real de uso de la API.

Hoy en día cualquiera puede publicar su código y levantar una API en cuestión de minutos. Nosotros vamos a levantar la API en Azure (de Microsoft).

### Azure

[Azure](https://azure.microsoft.com/free/?ref=microsoft.com&utm_source=microsoft.com&utm_medium=docs&utm_campaign=visualstudio) es un servicio de cómputo en la nube creado por *Microsoft* que ofrece una gran variedad de servicios del estilo de:
- Software as a Service [(SaaS)](https://en.wikipedia.org/wiki/Software_as_a_service)
- Platform as a Service [(PaaS)](https://en.wikipedia.org/wiki/Platform_as_a_service)
- Infrastructure as a Service [(IaaS)](https://en.wikipedia.org/wiki/Infrastructure_as_a_service)

Azure se puede usar para levantar nuestra API en la nube, en caso de que queramos llevar nuestra API para un producto.

### Cómo se levanta

No vamos a ir muy en detalle sobre como hacer esto porque cuesta plata usar **Azure**, aunque tienen una capa gratuita que se puede utilizar. Hay varios tutoriales sobre como hacerlo más en detalle, vamos a ir muy por arriba explicando los cambios necesarios para poder hacer esto.

Usamos algunos servicios de **Azure** como:
- [Azure App Service](https://docs.microsoft.com/en-us/azure/app-service/overview) --> Sirve para hostear la API, permite escalarla
- [Azure Database for Postgres](https://azure.microsoft.com/en-us/services/postgresql/) --> Va a ser la base de datos de la API

Los cambios y acciones no son muchos (son cambios pequeños al código, pero necesarios para usar *Azure*):
1. Tener el código en un repositorio de Github (no tiene que ser github, pero es gratis) --> Es necesario que el código esté en algún lugar en la nube guardado
2. Cambiar el `ALLOWED_HOSTS` --> Hay que cambiar para que sea `ALLOWED_HOSTS = ['*']
` porque vamos a tener la arquitectura de **Azure** y es necesario para esto
3. Cambiar la base de datos --> Vamos a usar PostgreSQL en vez de SQLite (que es la base default), ya que necesitamos un servicio de base de datos y es conveniente que esté todo en el mismo lugar (*Azure*):
    1. Instalar [psycopg2](https://pypi.org/project/psycopg2/) para poder conectarse a PostgreSQL
        ```bash
        pip install psycopg2
        ```
    2. Cambiar la configuración de la base de datos para que use PostgreSQL en vez de SQLite:
        ```python
        # Usamos variables de entorno por mayor seguridad
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': os.environ.get('DBNAME'), 
                'USER': os.environ.get('DBUSER'), 
                'PASSWORD': os.environ.get('DBPASS'),
                'HOST': os.environ.get('DBHOST'), 
                'PORT': '5432',
            }
        }
        ```
    3. Corregir una porción de código vieja que está en `api/admin.py` que genera un error al subir a *Azure*:
        ```python
        # Importamos el error que no se pudo hacer la operación
        from django.db.utils import ProgrammingError
        ...
        try:
        ...
        # Cambiar este except para que use ProgrammingError
        except ProgrammingError:
        ...
        ```
4. Alterar la configuración de `cs_api/settings.py` para agregar:
    ```python
    import os
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
    ```

Por la parte de Azure, es necesario:
1. Crear una **Azure App Service** para hostear la API, especificando que se usa Python como entorno para correr
2. Crear una **Azure Database for Postgres** para la base de datos, y guardar los nombres usados
3. Armar en el **App Service Plan** la pipeline de CI/CD para que se levante automáticamente

### Resultado

Luego de poder deployar todo correctamente, obtenemos una url de nuestra API `https://csitba.azurewebsites.net/`.

Esta API actualmente está corriendo, así que se puede usar de la misma manera que veníamos probando nuestra API original.

**NOTA:** La versión de la API levantada es una versión hecha hasta la parte de agregar fondos. El repositorio donde se puede encontrar el código de la API adaptado para usarse en Azure es [este](https://github.com/csitba/curso-web-backend-azure).

### Recursos

Hay una gran cantidad de tutoriales de Microsoft que explican como levantar una API en Django con Azure en mucho más detalle:
- [Cómo armar una API en Django con PostgreSQL - Medium](https://stackpython.medium.com/how-to-start-django-project-with-a-database-postgresql-aaa1d74659d8)
- [Ejemplo de aplicación de Django con Azure - Github](https://github.com/SunBuild/django-poll)
- [Cómo armar una API en Django con PostgreSQL - Azure App Service](https://azure.github.io/AppService/2017/05/10/Create-Django-Web-app-with-PostgreSQL.html)
- [Cómo deployar una API en Django con Azure App Services](https://docs.microsoft.com/en-us/azure/app-service/tutorial-python-postgresql-app?tabs=bash%2Cclone)
- [Armar una API básica en Django con Azure](https://stories.mlh.io/deploying-a-basic-django-app-using-azure-app-services-71ec3b21db08)
- [Serie de videos de Microsoft sobre APIs en Django con Azure](https://channel9.msdn.com/shows/Azure-Friday/Python-on-Azure-Part-1-Building-Django-apps-with-Visual-Studio-Code?ocid=AID754288&wt.mc_id=CFID0237)