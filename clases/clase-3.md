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