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

Vamos a partir de lo que estuvimos armando la clase anterior, así que en caso de que no hayas podido seguir la clase o tuviste problemas siguiendola, [aca](LINK) podés bajarte una copia del proyecto anterior (va a estar en un ZIP).

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