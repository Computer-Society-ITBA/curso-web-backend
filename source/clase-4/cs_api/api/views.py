# Importamos el decorator
from rest_framework.decorators import api_view, permission_classes
# Importamos los permisos
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
# Importamos nuestros forms y modelos
from api import forms, models, serializers, constants, pagination, extractor
# Importamos nuestro permiso
from api.permissions import IsAdmin, IsUser, IsOwner
# Importamos las transacciones
from django.db import transaction, IntegrityError
# Importamos la clase Group
from django.contrib.auth.models import Group
# Importamos al Paginator
from django.core.paginator import Paginator, EmptyPage
# Importamos para los queries
from django.db.models import Q

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
    # Extraemos el query param, ponemos None como default
    query = request.GET.get('q', None)
    # Estraemos los query de paginación, y si hay un error devolvemos eso
    page, page_size, err = extractor.extract_paging_from_request(
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


@api_view(['POST', 'GET'])
@permission_classes([IsUser])
def transaction_view(request):
    # Hacemos el caso de un GET y el caso de un POST
    if request.method == 'GET':
        return get_transactions(request)
    else:
        return create_transaction(request)


def get_transactions(request):
    # Extraemos query params de fechas, y si hay un error devolvemos eso
    inicio, fin, err = extractor.extract_limits_from_request(
        request=request)
    if err != None:
        return err
    # Estraemos los query de paginación, y si hay un error devolvemos eso
    page, page_size, err = extractor.extract_paging_from_request(
        request=request)
    if err != None:
        return err

    # No hay caso en que haya uno y no otro, así que en este caso es lo mismo si ponemos un and o un or
    if inicio != None and fin != None:
        # Hacemos 2 filtros, primero vemos transacciones del usuario en donde es destion u origen
        # Después filtramos por fechas y ordenamos por id descendente
        queryset = models.Transaction.objects.filter(
            (Q(destino=request.user) | Q(origen=request.user)), fecha_realizada__range=(inicio, fin)).order_by('-id')
    else:
        # Hacemos 1 solo filtro, con transacciones del usuario
        queryset = models.Transaction.objects.filter(
            (Q(destino=request.user) | Q(origen=request.user))).order_by('-id')

    # Usamos un try catch por si la página está vacía
    try:
        # Convertimos a Paginator
        query_paginator = Paginator(queryset, page_size)
        # Nos quedamos con la página que queremos
        query_data = query_paginator.page(page)
        # Serializamos a los usuarios
        serializer = serializers.TransactionSerializer(query_data, many=True)
        # Agregamos a los usuarios a la respuesta
        resp = Response(serializer.data)
        # Agregamos headers de paginación a la respuesta
        resp = pagination.add_paging_to_response(
            request, resp, query_data, page, query_paginator.num_pages)
        return resp
    except EmptyPage:
        return Response(status=status.HTTP_404_NOT_FOUND)


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
                tx = models.Transaction(
                    origen=request.user, destino=destino, cantidad=cantidad)
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