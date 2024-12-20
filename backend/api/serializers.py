from rest_framework import serializers
from .models import emprestimo




class LoginSerializer(serializers.Serializer):
    imagem = serializers.ImageField(required = False)


class LoanSerializer(serializers.Serializer):
    valor = serializers.CharField(max_length=255, required=True)
    duracao = serializers.CharField(max_length=255, required=True)
    salario = serializers.CharField(max_length=255, required=False)
    profissao = serializers.CharField(max_length=255, required=False)
    documentos = serializers.CharField(max_length=255, required=False)
    tiposempr = serializers.CharField(max_length=255, required=False)
    estado = serializers.ChoiceField(choices=[("por resolver", "Por Resolver"), ("resolvido", "Resolvido")], default="por resolver")


class BankLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()