---
layout: default
title:  "Clase 3"
description: "Clase 3 - Modelos en Detalle, Búsqueda y Paginación"
principal: false
---

# Clase 3

¡Bienvenidos a la clase número 3!

En esta clase vamos a ver como funcionan los modelos en detalle, como armar una búsqueda y paginación.

Los temas de esta clase son:
TODO TEMAS

***
***

## Setup

Vamos a partir de lo que estuvimos armando la clase anterior, así que en caso de que no hayas podido seguir la clase o tuviste problemas siguiendola, [aca](bases/base-clase-3.zip) podés bajarte una copia del proyecto anterior (va a estar en un ZIP).

**NOTA**: Si nos pudiste seguir no hace falta esto.

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

Creamos el superuser de nuevo:
```bash
python manage.py createsuperuser
```

Corremos la api para ver que todo ande bien:
```bash
python manage.py runserver
```

***
***

## Modelos

Reviendo la parte de modelos de la clase pasada, en Django nos referimos a los objetos como *Modelos*. Cada modelo hace referencia a una tabla o relación dentro de la base de datos.

Django usa un **ORM**, [*Object–Relational Mapping*](https://en.wikipedia.org/wiki/Object%E2%80%93relational_mapping), que es una técnica de programación que abstrae a la base de datos de los modelos que usamos. Significa que no necesitamos saber SQL para hacer cosas como insertar un objeto o borrarlo, y además nos abstrae de la base de datos que usamos, porque nos permite cambiar la base de datos (por ejemplo cambiar SQLite por PostgreSQL) sin necesidad de adaptar nada, se hace solo. Django también provee una gran variedad de métodos para interactuar con los modelos. Siempre nos vamos a referir a modelos, nunca a tablas ni nada similar.

Una ventaja de usar el ORM es que podemos acceder a los objetos relacionados usando el operador `.`. Por ejemplo, si una transacción está asociada a un usuario, partiendo de una instancia del modelo `Transaction`, podemos obtener al usuario haciendo esto, `my_transaction.user`, y eso nos devuelve el modelo del usuario.

Estos modelos los declaramos dentro del archivo `api/models.py`.

### Metodos de los Modelos

Django ofrece un montón de [métodos](https://docs.djangoproject.com/en/3.1/ref/models/instances) para interactuar con nuestros modelos, los más usados son:
- `save()` --> Sirve para guardar los cambios que se hicieron sobre la instancia de un modelo o guardar un nuevo objeto, se llama como `instance.save()`
- `delete()` --> Sirve para borrar la instancia del modelo, se llama como `isntance.delete()`
- `create()` --> Sirve para crear y guardar un nuevo objeto, se llama como `Model.objects.create(...)`, donde `Model` es el modelo que queremos crear

Hay muchos más métodos, pero los vamos a ver más adelante cuando hablemos de búsqueda.

### Campos de los Modelos

Los campos en los modelos se llaman [**fields**](https://docs.djangoproject.com/en/3.1/ref/models/fields/#model-field-types), y Django viene con una gran cantidad de estos que se pueden usar en los modelos. Los más comunes son:
- `BooleanField` --> Sirve para un campo booleano, True o False
- `CharField` --> Sirve para guardar texto
- `DateField` --> Sirve para guardar fechas
- `DateTimeField` --> Sirve para guardar fecha y hora
- `DecimalField` --> Sirve para guardar números decimales de precisión arbitraria
- `EmailField` --> Sirve exactamente para un email
- `FloatField` --> Sirve para números decimales con precisión `float`
- `IntegerField` --> Sirve para números enteros
- `AutoField` --> Sirve para especificar números autoincrementales como IDs, pero Django por default agrega IDs, así que no hace falta usarlo

También permite especificar campos de relaciones, como relaciones con otros objetos, se usan (entre muchos otros):
- `ForeignKey` --> Sirve para especificar el modelo relacionado
- `OneToOneField` --> Sirve para especificar relaciones 1 a 1

***

## Creando nuevos modelos

Vamos a agregarle un nuevo modelo a nuestra API, el modelo `Transaction`. Queremos que las personas puedan empezar a usar nuestra API para transferir dinero, por lo que tenemos que agregar nuestro nuevo modelo.

En `api/models.py` agregamos nuestro modelo de `Transaction`:
```python
class Transaction(models.Model):
    # Usuario que origina la transacción, especificamos el nombre porque sinó tira un error
    origen = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='origen')
    # Usuario que recibe la transacción
    destino = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='destino')
    # Cantidad de dinero transferida
    cantidad = models.FloatField(blank=False, null=False, default=0.0)
    # Fecha en que se hace la transacción
    fecha_realizada = models.DateTimeField(blank=False, null=False, auto_now_add=True)
```

Nuestro modelo de `Transaction` tiene un `origen` y `destino`, que son usuarios de la API. Usamos `on_delete=models.SET_NULL` porque no queremos perder el registro de transacciones si se borra un usuario, si bien va a quedar `NULL`, queda el registro para el otro usuario. La `fecha_realizada` usa `auto_now_add=True` para que se ponga solo con la fecha en que creamos el nuevo objeto.

Dado que no queremos que se pierda toda la información de la transacción cuando se borra un usuario, tenemos que hacer algo. Nos conviene pasar de *borrado físico* a un *borrado lógico* de los usuarios. El *borrado físico* significa que físicamente borramos al usuario de la base de datos, mientras que el *borrado lógico* significa que usamos algún campo del usuario para marcarlo como inactivo o borrado. Por suerte los usuarios de Django tienen un campo que se llama `is_active`. Cambiamos el código para crear un usuario para que ahora en vez de `user.delete()` haga esto:
```python
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
        # Hacemos que no esté activo en vez de borrado físico
        user.is_active = False
        user.save()
        # Devolvemos que no hay contenido porque lo pudimos borrar
        return Response(status=status.HTTP_204_NO_CONTENT)
    except models.User.DoesNotExist:
        # Si no existe le damos un 404
        return Response(status=status.HTTP_404_NOT_FOUND)
```

Vamos a aprovechar para también registrar este modelo para verlo en la consola de admin, en `api/admin.py` agregamos:
```python
admin.site.register(models.Transaction)
```

Después de hacer esto, como agregamos un modelo, tenemos que hacer las migraciones:
```bash
python manage.py makemigrations && python manage.py migrate
```

***

## Creando transacciones

Vamos a armar nuestro nuevo endpoint para poder crear transacciones. Este endpoint va a estar en la url `api/transactions` con un POST, y recibe en el body un campo `destino` y un campo `cantidad`.

### Form

Necesitamos un *Form* porque vamos a estar usando un POST. Adentro de `api/forms.py` vamos a agregar nuestro nuevo form:
```python
# Importamos los forms
from django import forms

# Nuestra form extiende de "Form" y no tiene un modelo asociado
class CreateTransactionForm(forms.Form):
    # Campo con el ID de la cuenta destino, no puede ser menor que 1
    destino = forms.IntegerField(min_value=1)
    # Campo para la cantidad, no puede ser menor que 0
    cantidad = forms.FloatField(min_value=0)

    def clean_destino(self):
        try:
            # Buscamos usuarios que tengan ese id
            user = models.User.objects.get(id=self.cleaned_data.get('destino'))
            # Si no existe el usuario, tiramos un error
            # Si el usuario no está activo, le decimos que no existe al otro
            # No tiene por que saber que ese usuario está borrado
            # Si el usuario no es user, no dejamos que se haga
            if user == None:
                raise ValidationError("No existe el destinatario.")
            elif not user.is_active:
                raise ValidationError("No existe el destinatario.")
            elif user.groups.all()[0].name != constants.GROUP_USER:
                raise ValidationError("El destinatario no es un usuario.")
            # Si está todo bien devuelvo el destino
            return self.cleaned_data.get('destino')
        except models.User.DoesNotExist:
            raise ValidationError("No existe el destinatario.")
```

En este form no usamos un modelo porque no es necesario, para crear el modelo `Transaction` necesitamos que el usuario `origen` esté, pero desde el form no podemos acceder a eso.

### Permiso

Queremos hacer que solo los usuarios del grupo `user` puedan armar transacciones, y para eso necesitamos definir un nuevo permiso. 

En `api/permissions.py` vamos a agregar nuestro nuevo permiso `IsUser`:
```python
# La clase IsUser es nuestro permiso, que tiene que extender de BasePermission para que sea un permiso
class IsUser(BasePermission):
    # Mensaje de error que va a devolver
    message = "El usuario no es user"

    def has_permission(self, request, view):
        # Si no tiene grupos le decimos que no de una
        if not request.user.groups.exists():
            return False
        return request.user.groups.all()[0].name == constants.GROUP_USER
```

### Serializer

Queremos devolver la transacción creada, al igual que como hicimos con el usuario, así que tenemos que agregar un serializer en `api/serializers.py`:
```python
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Transaction
        fields = ('id', 'origen', 'destino', 'cantidad', 'fecha_realizada')
```
Incluye el `id`, la `fecha_realizada` y la información de participantes y cantidad.

### View Funcional

Con nuestro permiso, modelo, form y serializer estamos listos para crear la función que arma la transacción. La creamos en `api/views.py`:
```python
# Importamos nuestro permiso
from api.permissions import IsAdmin, IsUser
# Importamos las transacciones
from django.db import transaction, IntegrityError

@api_view(['POST'])
@permission_classes([IsUser])
def create_transaction(request):
    # Creamos el form
    form = forms.CreateTransactionForm(request.POST)
    # Vemos si es válido
    if form.is_valid():
        # Obteniendo el usuario destino y la cantidad
        destino = models.User.objects.get(id=form.cleaned_data['destino'])
        cantidad = form.cleaned_data['cantidad']
        # Usamos un bloque transaccional para evitar problemas
        try:
            with transaction.atomic():
                # Vemos que tenga plata suficiente
                if cantidad > request.user.account.balance:
                    return Response({"error": "Balance insuficiente"}, status=status.HTTP_400_BAD_REQUEST)
                # Creamos la transaccion
                tx = models.Transaction(origen=request.user, destino=destino, cantidad=cantidad)
                # Actualizamos los balances
                request.user.account.balance -= cantidad
                destino.account += cantidad
                # Guardamos los cambios
                tx.save()
                request.user.account.save()
                destino.account.save()
                # Nuestra respuesta
                return Response(serializers.TransactionSerializer(tx, many=False).data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({"error": "Error transfiriendo fondos"}, status=status.HTTP_400_BAD_REQUEST)        
    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
```

Hay varias cosas para mencionar de este código:
- Usamos un decorator (`@permission_classes([IsUser])`) para definir el permiso.
- Usamos una transacción (de base de datos, no nuestro modelo) para poder hacer la operacion. Esto lo hacemos porque la transacción nos asegura que pasa todo o no pasa nada. No queremos que la transacción no ocurra pero a un usuario le saquemos plata, entonces la transacción de la base de datos nos permite hacer esto. Lo que se hace dentro de la transacción está dentro del bloque `with transaction.atomic():` y si hay un error es del tipo `IntegrityError`.

### Registrar URL

Con la función creada, podemos ir a `cs_api/urls.py` a registrar el endpoint:
```python
urlpatterns = [
    ...
    path('api/transactions', views.create_transaction, name="create_transaction"),
    ...,
]
```

### Probamos las transacciones

Para poder probar las transacciones necesitamos, 2 usuarios de tipo `user` y agregarles balance a esos usuarios. 

Para agregarles balance se puede editar por ahora desde la consola de admin yendo a la parte de `Account`.

Para probar crear transacciones se puede usar el siguiente curl (mis usuarios de prueba tenían id 5 y 6):
```bash
curl -X POST -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo1LCJ1c2VybmFtZSI6InRlc3R1c2VyMSIsImV4cCI6MTYxMjEyMTcwMSwiZW1haWwiOiJoaXJzY2hnb256YWxvK3Rlc3R1c2VyMUBnbWFpbC5jb20ifQ.UkRuDXtdtv2Rag5oqoUk3nMiAXGwszP76BLE7Gzh7vo"  -F 'destino=6' -F 'cantidad=100' http://localhost:8000/api/transactions
```

Podemos también probar que pasa cuando mandamos cosas que no corresponden:
```bash
# Cantidad muy grande
curl -X POST -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo1LCJ1c2VybmFtZSI6InRlc3R1c2VyMSIsImV4cCI6MTYxMjEyMjA4OCwiZW1haWwiOiJoaXJzY2hnb256YWxvK3Rlc3R1c2VyMUBnbWFpbC5jb20ifQ.dAekC-_5QNuTA8uDpY7naFNoOZi44ZlcecdjSxNa12w"  -F 'destino=6' -F 'cantidad=10000' http://localhost:8000/api/transactions
# Sin cantidad
curl -X POST -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo1LCJ1c2VybmFtZSI6InRlc3R1c2VyMSIsImV4cCI6MTYxMjEyMjA4OCwiZW1haWwiOiJoaXJzY2hnb256YWxvK3Rlc3R1c2VyMUBnbWFpbC5jb20ifQ.dAekC-_5QNuTA8uDpY7naFNoOZi44ZlcecdjSxNa12w"  -F 'destino=6' http://localhost:8000/api/transactions
# Usuario destinatario es admin
curl -X POST -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo1LCJ1c2VybmFtZSI6InRlc3R1c2VyMSIsImV4cCI6MTYxMjEyMjA4OCwiZW1haWwiOiJoaXJzY2hnb256YWxvK3Rlc3R1c2VyMUBnbWFpbC5jb20ifQ.dAekC-_5QNuTA8uDpY7naFNoOZi44ZlcecdjSxNa12w"  -F 'destino=1' -F 'cantidad=10000' http://localhost:8000/api/transactions
# Usuario destinatario no existe
curl -X POST -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo1LCJ1c2VybmFtZSI6InRlc3R1c2VyMSIsImV4cCI6MTYxMjEyMjA4OCwiZW1haWwiOiJoaXJzY2hnb256YWxvK3Rlc3R1c2VyMUBnbWFpbC5jb20ifQ.dAekC-_5QNuTA8uDpY7naFNoOZi44ZlcecdjSxNa12w"  -F 'destino=10' -F 'cantidad=10000' http://localhost:8000/api/transactions
```

***

## Busqueda

Ahora que ya podemos armar transacciones, estaría bueno poder buscar a usuarios para poder armar las transacciones. Ahora mismo es un poco difícil encontrar al usuario que buscamos, sería más cómodo si pudieramos buscar por el nombre de usuario por ejemplo.

### Como funciona la busqueda

Para poder armar una búsqueda, lo primero que hay que hacer es definir los campos por los que uno va a poder buscar. En nuestro caso (enfocándonos en usuarios) la búsqueda se hace por `username`.

Para poder enviarle a la API la búsqueda que queremos hacer, hay que poder especificar lo que queremos buscar en sí, y para que sea bien correcta nuestra implementación, deberíamos poder buscar con el endpoint `api/accounts`. Para poder hacer esto usamos *Query Params*.

Vamos a definir un *Query Param* que le vamos a enviar a al endpoint para que pueda hacer la búsqueda. Un buen *Query Param* puede ser la letra `q`, representado un `query`.

### Django y Busqueda

Dentro de los muchos métodos que Django provee para nuestros modelos, hay una gran cantidad que son para realizar [queries](https://docs.djangoproject.com/en/3.1/topics/db/queries/) (o búsquedas), los más usados son:
- `all()` --> Sirve para buscar todos los objetos para un modelo, se llama como `Model.objects.all()`
- `filter(...)` --> Sirve para quedarse con los objetos que cumplen cierta condición, se llama como `Model.objects.filter(...)`
- `exclude(...)` --> Es como `filter` pero te quedás con los que NO cumplen cierta condición, se llama como `Model.objects.exclude(...)`
- `get(...)` --> Sirve para obtener *1 solo* objeto, si hay más de uno da un error, se llama como `Model.objects.get(...)`

Los métodos `filter` y `exclude` son métodos de querying, entonces lo que se puede hacer es especificar condiciones, como por ejemplo que sea mayor o que contenga cierta palabra. Estas condiciones se agregan de la siguiente forma a los métodos:
```python
Model.objects.filter(CAMPO__CONDICION=VALOR)
```
En donde `CAMPO` es el nombre del campo del modelo (se puede acceder a los relacionados usando `__` en el medio, si el modelo tiene a un *User* relacionado, se puede acceder al ID del usuario como `user__id`), `CONDICION` es la condición (puede ser `lte` (less than or equal) o `icontains` (contains case-insensitive) y hay muchas más), y `VALOR` es el valor que le damos de referencia.

En nuestro caso, que la búsqueda de usuarios se hace por `username`, sería algo así:
```python
users = models.User.objects.filter(username__icontains="test")
```

### Implementando la busqueda

No requiere un cambio muy grande en la API, simplemente tenemos que editar la función `get_accounts` de `api/views.py`:
```python
def get_accounts(request):
    # Chequear que no sea anónimo
    if request.user.is_anonymous:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    # Extraemos el query param, ponemos None como default
    query = request.GET.get('q', None)
    # Definimos el set como todos los usuarios
    queryset = models.User.objects.all()
    # Si hay query, agregamos el filtro, sino usa todos
    if query != None:
        # Hacemos icontains sobre el username, y ordenamos por id, el "-" indica que es descendiente
        queryset = queryset.filter(username__icontains=query).order_by('-id')
    # Obtenemos todos los usuarios y los serializamos
    users = serializers.UserSerializer(queryset, many=True).data
    # Agregamos los datos a la respuesta
    return Response(users, status=status.HTTP_200_OK)
```

Simplemente extraemos el query param `q`, y si vemos que es diferente de `None` (que es el default), corremos el filtro. Ordenamos por `id` descendente para que tenga un orden de más nuevo a más viejo. También, como son encadenables los filtros, podemos hacer primero el `all` y si hay un query, podemos encadenarle el `filter`.

Para probar este nuevo query lo que se puede hacer es:
```bash
curl -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo1LCJ1c2VybmFtZSI6InRlc3R1c2VyMSIsImV4cCI6MTYxMjEyOTU3MiwiZW1haWwiOiJoaXJzY2hnb256YWxvK3Rlc3R1c2VyMUBnbWFpbC5jb20ifQ.Lteb8xlmcCjCCbYUtcuMR2u06H9TgjnauWQRAVJ94N4" http://localhost:8000/api/accounts?q=test
```
Y si probamos con diferentes búsquedas vemos que funciona.

***

## Paginacion

Como está ahora nuestra API, si no filtramos los usuarios obtenemos todos los que tenemos. Esto es poco práctico, si tenemos 1 millón de usuarios nos vamos a traer la base de datos entera y no estaría bueno.

Paginación es separar nuestros resultados en **páginas**, es decir, cuando alguien pide resultados va a ver solo parte de los resultados, y si quiere ver más, tendrá que pedir páginas diferentes.

### Como funciona la paginacion

La paginación, al igual que la búsqueda, se puede hacer simplemente agregando 2 *Query Param* a nuestro endpoint de búsqueda. Vamos a agregar el parámetro `p` (indica la página que queremos) y el parámetro `s` (indica cuantos elementos por página mostramos).

Esto hace que nuestra API sea mucho más eficiente y cómoda de usar para los usuarios.

Y también nuestra API ahora va a devolver algo más además de los resultados, va a tener unos *Header* especiales que contienen links a otras páginas para facilitar la navegación. Va a contener 4 *Header*s:
- **first** --> Link a la primera página
- **prev** --> Link a la página anterior
- **next** --> Link a la página siguiente
- **last** --> Link a la última página

### Django y paginacion

Django provee algo llamado `Paginator`, que se puede usar para paginar nuestros resultados, de forma que sea muy simple implementarlo.

Este `Paginator` recibe la lista de objetos que tiene que paginar y los tamaños de páginas, para devolvernos un objeto al que le podemos pedir nuestras diferentes páginas.

### Implementando paginacion

Para implementar nuestra paginación vamos a necesitar ayuda de 3 funciones extra que vamos a crear en un archivo que se llame `api/pagination.py`. Vamos a armar una función que agregue los headers de paginación, otra que cambie el parámetro viejo de paginación por el nuevo que queremos para los headers, y una última que extraiga los headers de paginación (para poder reusarla después):
```python
# Importamos para parsear la url
import urllib.parse as urlparse
# Importamos nuestras constantes
from api import constants
from rest_framework.response import Response
from rest_framework import status

# Agrega headers de paginación a la response
def add_paging_to_response(request, response, query_data, page, total_pages):
    # Extraemos la URL
    complete_url = request.build_absolute_uri()
    # Usamos un pequeño "algoritmo" para determinar que headers mostrar
    # Si tiene próxima, la agrego
    if query_data.has_next():
        response[constants.HEADER_NEXT] = replace_page_param(
            complete_url, query_data.next_page_number())
    # Si tiene anterior, la agrego
    if query_data.has_previous():
        response[constants.HEADER_PREV] = replace_page_param(
            complete_url, query_data.previous_page_number())
    # Si no estamos en la última página, y tampoco en la anteúltima, lo agrego
    if page < total_pages and (query_data.has_next() and query_data.next_page_number() != total_pages):
        response[constants.HEADER_LAST] = replace_page_param(
            complete_url, total_pages)
    # Si no estamos en la página 1 y tiene una página anterior que es diferente de 1, la agregamos
    if page > 1 and (query_data.has_previous() and query_data.previous_page_number() != 1):
        response[constants.HEADER_FIRST] = replace_page_param(complete_url, 1)
    return response

# Reemplaza el parámetro de la p en la url dada
def replace_page_param(url, new_page):
    # Parseamos la URL
    parsed = urlparse.urlparse(url)
    # Extraemos los query params
    querys = parsed.query.split("&")
    # Flag para ver si vino o no el param de la página
    has_page = False
    # Buscamos el param de la página
    for i in range(len(querys)):
        # Separamos para ver si empieza con "p"
        parts = querys[i].split('=')
        if parts[0] == 'p':
            # Cambiamos el parámetro viejo por el nuevo
            querys[i] = 'p=' + str(new_page)
            has_page = True

    # Si no vino con página lo agregamos
    if not has_page:
        querys.append("p=" + str(new_page))

    # Reconstruimos los query params
    new_query = "&".join(["{}".format(query) for query in querys])
    # Reconstruimos la URL
    parsed = parsed._replace(query=new_query)

    return urlparse.urlunparse(parsed)

# Extrae y valida los headers de paginación
def extract_paging_from_request(request, page_default=1, page_size_default=6):
    try:
        page = int(request.GET.get('p', page_default))
        page_size = int(request.GET.get('s', page_size_default))
    except ValueError:
        return None, None, Response(status=status.HTTP_400_BAD_REQUEST)
    return page, page_size, None
```

La función `add_paging_to_response` se ocupa de agregar los headers necesarios según un pequeño algoritmo, mientras que `replace_page_param` se ocupa de ayudarla a construir la URL bien.

También agregamos unas nuevas constantes a nuestro archivo de constantes (`api/constants.py`):
```python
HEADER_LAST = "last"
HEADER_FIRST = "first"
HEADER_NEXT = "next"
HEADER_PREV = "prev"
```

Del lado de la función en `api/views.py`, hay que hacer unos pequeños cambios para implementar la paginación:
```python
def get_accounts(request):
    # Chequear que no sea anónimo
    if request.user.is_anonymous:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    # Extraemos el query param, ponemos None como default
    query = request.GET.get('q', None)
    # Estraemos los query de paginación, y si hay un error devolvemos eso
    page, page_size, err = pagination.extract_paging_from_request(
        request=request)
    if err != None:
        return err

    # Si hay query, agregamos el filtro, sino usa todos
    if query != None:
        # Hacemos icontains sobre el username, y ordenamos por id, el "-" indica que es descendiente
        queryset = models.User.objects.filter(
            username__icontains=query).order_by('-id')
    else:
        # Definimos el set como todos los usuarios
        queryset = models.User.objects.all().order_by('-id')

    # Usamos un try catch por si la página está vacía
    try:
        # Convertimos a Paginator
        query_paginator = Paginator(queryset, page_size)
        # Nos quedamos con la página que queremos
        query_data = query_paginator.page(page)
        # Serializamos a los usuarios
        serializer = serializers.UserSerializer(query_data, many=True)
        # Agregamos a los usuarios a la respuesta
        resp = Response(serializer.data)
        # Agregamos headers de paginación a la respuesta
        resp = pagination.add_paging_to_response(
            request, resp, query_data, page, query_paginator.num_pages)
        return resp
    except EmptyPage:
        return Response(status=status.HTTP_404_NOT_FOUND)
```

Usamos la función `extract_paging_from_request` para extraer los query param de paginación, luego dependiendo de si hay un query o no, hacemos el filtro o no. Con los datos, generamos el paginator y nos quedamos con la página que queremos. Serializamos los resultados y agregamos lo headers de paginación a la respuesta.

Para probar lo que se puede hacer es:
```bash
curl -i -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo1LCJ1c2VybmFtZSI6InRlc3R1c2VyMSIsImV4cCI6MTYxMjEyOTU3MiwiZW1haWwiOiJoaXJzY2hnb256YWxvK3Rlc3R1c2VyMUBnbWFpbC5jb20ifQ.Lteb8xlmcCjCCbYUtcuMR2u06H9TgjnauWQRAVJ94N4" 'http://localhost:8000/api/accounts?p=1&s=1'
```