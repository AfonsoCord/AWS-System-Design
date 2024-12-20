from rest_framework import serializers
from .models import emprestimo



class Simulador(serializers.ModelSerializer):
    class Meta:
        fields = ["id","valor","duracao","salario","profissao","documentos","tipoemprestimo","tempo","person"]
        

class LoginSerializer(serializers.Serializer):
    imagem = serializers.ImageField(required = False)


class LoanSerializer(serializers.Serializer):
    valor = serializers.CharField(max_length=255, required=True)
    duracao = serializers.CharField(max_length=255, required=True)
    salario = serializers.CharField(max_length=255, required=True)
    profissao = serializers.CharField(max_length=255, required=True)
    documentos = serializers.CharField(max_length=255, required=True)
    tiposempr = serializers.CharField(max_length=255, required=True)
    estado = serializers.ChoiceField(choices=[("por resolver", "Por Resolver"), ("resolvido", "Resolvido")], default="por resolver")


class BankLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()