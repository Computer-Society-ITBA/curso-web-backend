from django.test import TestCase
from django.contrib.auth.models import Group
from api import constants, models
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status


# Dado el token, agrega el header a la request
def api_authorization(obj, token):
    obj.client.credentials(
        HTTP_AUTHORIZATION="JWT " + token)

# Crea los diferentes grupos
def create_groups():
    group_user = Group.objects.create(name=constants.GROUP_USER)
    group_admin = Group.objects.create(name=constants.GROUP_ADMIN)
    return group_user, group_admin

# Crea a un usuario, le pone los grupos
# Crea la cuenta asociada
# Recibe:
# - group -->  grupo que se le pone al usuario
# - username --> nombre del usuario para usar
# - active --> define si el usuario está activo
# - password --> contraseña del usuario
def create_user(group, username, password, active):
    # Crea al usuario
    user = User.objects.create_user(
        username=username, password=password, is_active=active)
    # Le pone el grupo
    user.groups.add(group)
    # Crea la account relacionada
    models.Account.objects.create(user=user)
    return user

# Genera un usuario con un token
def create_user_with_token(group, username, password, client):
    # Crea al usuario
    user = User.objects.create_user(
        username=username, password=password, is_active=True)
    # Le pone el grupo
    user.groups.add(group)
    # Crea la account relacionada
    models.Account.objects.create(user=user)
    # Genera un token
    user_token = get_jwt_token(client, username, password)
    return user, user_token

# Hace una request para obtener el token
def get_jwt_token(client, username, password):
    # Hace un post para el token
    response = client.post("/api/auth/login", {"username": username, "password": password}, format='json')
    return response.data["token"]

# Prueba casos de logueo donde el usuario está activo
class ActiveUserLoginTestCase(APITestCase):
    def setUp(self):
        u, a = create_groups()
        self.username = "testuser"
        self.password = "contraseña123456"
        self.user = create_user(u, self.username, self.password, True)

    # Prueba el login correcto
    def test_login_ok(self):
        data = {"username": self.username, "password": self.password}
        response = self.client.post("/api/auth/login", data)
        # Esperamos un 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Vemos que no sea vacío el token
        self.assertNotEquals(response.data["token"], "")
    
    # Prueba el login error cuando está mal el usuario o password
    def test_login_invalid_credentials(self):
        data = {"username": self.username, "password": "esto está mal"}
        response = self.client.post("/api/auth/login", data)
        # Esperamos un 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Esperamos que no venga un token en la respuesta
        self.assertTrue(not "token" in response.data)

# Prueba casos donde el usuario está inactivo
class InactiveUserLoginTestCase(APITestCase):
    def setUp(self):
        u, a = create_groups()
        self.username = "testuser"
        self.password = "contraseña123456"
        self.user = create_user(u, self.username, self.password, False)
    
    # Prueba el login error cuando el user está inactivo
    def test_login_invalid_credentials(self):
        data = {"username": self.username, "password": self.password}
        response = self.client.post("/api/auth/login", data)
        # Esperamos un 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Esperamos que no venga un token en la respuesta
        self.assertTrue(not "token" in response.data)

# Prueba casos de traer los usuarios de la API
class UserRecoveryTestCase(APITestCase):
    def setUp(self):
        u, a = create_groups()
        self.username = "testuser"
        self.password = "contraseña123456"
        self.user, self.user_token = create_user_with_token(u, self.username, self.password, self.client)
        api_authorization(self, self.user_token)
    
    # Prueba el login error cuando el user está inactivo
    def test_users_get_ok(self):
        response = self.client.get("/api/accounts")
        # Esperamos un 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Esperamos que haya 1 solo usuario
        self.assertEquals(len(response.data), 1)

    # Prueba el error del endpoint si el usuario no tiene token
    def test_users_get_without_token(self):
        # Aseguramos que no haya un usuario autenticado
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/accounts")
        # Esperamos un 401
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)