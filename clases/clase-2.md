---
layout: default
title:  "Clase 2"
description: "Clase 2 - Usuarios, autenticación y permisos"
principal: false
---

# Clase 2

¡Bienvenidos a la clase número 2!

En esta clase vamos a ver como crear usuarios, como autenticarlos y como crear roles para los mismos.

Los temas de esta clase son:
  * [Qué es una API](#que-es-una-api)
  * [Cómo se usa una API](#como-se-usa-una-api)
  * [Qué significa ser REST](#que-significa-ser-rest)
  * [Qué es Django](#que-es-django)
  * [Cómo se arma un endpoint](#como-se-arma-un-endpoint)

***
***

## Setup

Vamos a partir de lo que estuvimos armando la clase anterior, así que en caso de que no hayas podido seguir la clase o tuviste problemas siguiendola, [aca](bases/base-clase-2.zip) podés bajarte una copia del proyecto anterior (va a estar en un ZIP).

**NOTA**: Si nos pudiste seguir, no vamos a usar los endpoints de prueba que armamos, así que podes borrar las funciones de la view (`api/views.py`) y los urls (`cs_api/urls.py`) y no tenés que hacer esta configuración.

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

## Que es la Autenticacion

Vamos a empezar diferenciando *Autenticación* y *Autorización*.

**Autenticación** --> Es el acto de validar que un usuario es quien dice ser, y si bien hay muchas formas de hacer esto, en nuestro caso vamos a estar autenticando a un usuario con un *nombre de usuario* + *contraseña*.

**Autorización** --> Es el proceso por el que un sistema (nuestra API) da permiso a un usuario de realizar una acción. Para que la API pueda determinar si tenemos permiso, tenemos que pasarle algo que indique que somos quien decimos ser, y que tenemos permisos.

En este caso, la forma de completar la autorización que vamos a usar es mediante **Tokens**. Una vez que nos autenticamos con la API, nos va a dar un *Token* que vamos a tener que usar en las requests que hagamos, para indicarle que somos nosotros y nos autorice a operar.

Este *Token* lo vamos a enviar en un header de la request de la siguiente manera: 
```bash
Authorization: Bearer <TOKEN>
```

***

## JWT Tokens

Hay muchos diferentes tipos de *Tokens*, pero nosotros queremos que nuestra API sea realmente REST, por lo que vamos a usar **JWT Tokens** (*Jason Web Tokens*).

Estos *Tokens* son especiales porque permiten autorizar al usuario con solo el token y no hace falta guardar información del *Token* en la base de datos.

### Como se arma un JWT Token

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

### Como funciona en nuestro caso

En nuestro caso, cuando hagamos un *log in*, la API va a generar un JWT Token para el usuario y es lo que nos responde si el log in fue exitoso.

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

Los [*Forms*](https://docs.djangoproject.com/en/3.1/topics/forms/) están hechos con el objetivo de escribir el form en Python y que luego se renderize como un HTML, pero no vamos a usar eso porque estamos armando una API REST. Se les puede agregar validaciones y asociar a modelos. Los declaramos en `api/forms.py`.

Nosotros vamos a usarlos de la siguiente manera, *Serializers* para devolver datos, y *Forms* para recibir datos. De esta forma, las validaciones solo son necesarias en los *Forms*, y los *Serializers* nos ocupamos de que sean la forma en la que nuestros modelos se representan al exterior.

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

Para extender al usuario vamos a empezar agregando nuestro modelo `Account` en `api/models.py`, que es lo que vamos a usar para extender al usuario:
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

Como agregamos un modelo hay que hacer las migraciones de nuevo:
```bash
python manage.py makemigrations && python manage.py migrate
```

Si corremos la API (`python manage.py runserver`), debería funcionar todo como antes, no deberíamos ver cambios.