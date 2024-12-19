from rest_framework import serializers
from .models import emprestimo



class Simulador(serializers.ModelSerializer):
    class Meta:
        fields = ["id","valor","duracao","salario","profissao","documentos","tipoemprestimo","tempo","person"]
        

class LoginSerializer(serializers.Serializer):
    imagem = serializers.ImageField(required = False)


class LoanSerializer(serializers.Serializer):
    Quantia = serializers.FloatField()
    Tempo = serializers.IntegerField()


class BankLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()