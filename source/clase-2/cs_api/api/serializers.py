from rest_framework import serializers
from django.contrib.auth.models import User

# Definimos un serializer que hereda de "ModelSerializer"
class UserSerializer(serializers.ModelSerializer):
    # En Meta ponemos que el modelo es el usuario
    # Ponemos que solo queremos esos 4 campos
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'is_active')