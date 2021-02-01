from rest_framework import serializers
from django.contrib.auth.models import User
from api import models, constants

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

class GroupSerializer(serializers.Serializer):
    # Definimos que solo tiene el nombre
    name = serializers.CharField(required=True)
    # Definimos la validación
    def validate(self, data):
        if data['name'] not in [constants.GROUP_ADMIN, constants.GROUP_USER]:
            raise serializers.ValidationError(
                "Grupo Inválido")
        return data

class UserDetailsSerializer(serializers.ModelSerializer):
    # Definimos los grupos con un serializer más para controlar la representación
    groups = GroupSerializer(many=True)
    # Definimos campos como read_only 
    id = serializers.IntegerField(read_only=True)
    email = serializers.CharField(read_only=True)
    username = serializers.CharField(read_only=True)
    # Definimos balance como un float field con un source indicando de donde sale
    balance = serializers.FloatField(source="account.balance", label="balance")

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'groups', 'balance')

    # Agregamos el "validate" para ver que no estén tratando de sacar balance
    def validate(self, data):
        # Usamos un context, que es algo que se le puede pasar al serializer al momento de instanciarlo
        if data['account']['balance'] < self.context['user'].account.balance:
            raise serializers.ValidationError(
                "Invalid balance, cannot be less than current")
        return data