from rest_framework import serializers
from django.contrib.auth.models import User
from api import models

# Definimos un serializer que hereda de "ModelSerializer"
class UserSerializer(serializers.ModelSerializer):
    # En Meta ponemos que el modelo es el usuario
    # Ponemos que solo queremos esos 4 campos
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'is_active')

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Transaction
        fields = ('id', 'origen', 'destino', 'cantidad', 'fecha_realizada')