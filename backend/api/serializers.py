from django.contrib.auth.models import User
from rest_framework import serializers
from .models import emprestimo

class Simulador(serializers.ModelSerializer):
    class Meta:
        model= User
        fields = ["id","valor","duracao","salario","profissao","documentos","tipoemprestimo","tempo","person"]
        

class LoginSerializer(serializers.Serializer):
    nome = serializers.CharField()
    id_cara = serializers.CharField()