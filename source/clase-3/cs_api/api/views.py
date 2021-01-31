# Importamos el decorator
from rest_framework.decorators import api_view, permission_classes
# Importamos los permisos
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
# Importamos nuestros forms y modelos
from api import forms, models, serializers, constants
# Importamos nuestro permiso
from api.permissions import IsAdmin, IsUser
# Importamos las transacciones
from django.db import transaction, IntegrityError
# Importamos la clase Group
from django.contrib.auth.models import Group

# Esta función es la que registramos en los urls
@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
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
        # Agregamos por default el grupo user a todos los usuarios
        user.groups.add(Group.objects.get(name=constants.GROUP_USER))
        # Creamos la Account que va con el usuario, y le pasamos el usuario que acabamos de crear
        models.Account.objects.create(user=user)
        # Respondemos con los datos del serializer, le pasamos nuestro user y le decimos que es uno solo, y depués nos quedamos con la "data" del serializer
        return Response(serializers.UserSerializer(user, many=False).data, status=status.HTTP_201_CREATED)
    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

def get_accounts(request):
    # Chequear que no sea anónimo
    if request.user.is_anonymous:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    # Obtenemos todos los usuarios y los serializamos
    users = serializers.UserSerializer(models.User.objects.all(), many=True).data
    # Agregamos los datos a la respuesta
    return Response(users, status=status.HTTP_200_OK)

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

@api_view(['POST'])
@permission_classes([IsUser])
def create_transaction(request):
    # Creamos el form
    form = forms.CreateTransactionForm(request.POST)
    # Vemos si es válido
    if form.is_valid():
        # Obteniendo el usuario destino y la canitdad
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
                destino.account.balance += cantidad
                # Guardamos los cambios
                tx.save()
                request.user.account.save()
                destino.account.save()
                # Nuestra respuesta
                return Response(serializers.TransactionSerializer(tx, many=False).data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({"error": "Error transfiriendo fondos"}, status=status.HTTP_400_BAD_REQUEST)        
    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)