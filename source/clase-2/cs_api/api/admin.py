from django.contrib import admin
# Importamos nuestros modelos
from api import models, constants
# Importamos el modelo de Group
from django.contrib.auth.models import Group
# Registramos nuestro modelo
admin.site.register(models.Account)
# Creamos el grupo de ADMIN
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
