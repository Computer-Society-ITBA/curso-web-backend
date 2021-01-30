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