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
    salario = serializers.CharField(max_length=255, required=False)
    profissao = serializers.CharField(max_length=255, required=False)
    documentos = serializers.CharField(max_length=255, required=False)
    tiposempr = serializers.CharField(max_length=255, required=False)
    estado = serializers.ChoiceField(choices=[("por resolver", "Por Resolver"), ("resolvido", "Resolvido")], default="por resolver")

    def create(self, validated_data):
        return emprestimo(**validated_data)
    
    def __init__(self, instance=None, data=..., **kwargs):
        super().__init__(instance, data, **kwargs)



class BankLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()