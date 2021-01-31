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

# La clase IsUser es nuestro permiso, que tiene que extender de BasePermission para que sea un permiso
class IsUser(BasePermission):
    # Mensaje de error que va a devolver
    message = "El usuario no es user"

    def has_permission(self, request, view):
        # Si no tiene grupos le decimos que no de una
        if not request.user.groups.exists():
            return False
        return request.user.groups.all()[0].name == constants.GROUP_USER