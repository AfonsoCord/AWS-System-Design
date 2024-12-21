from rest_framework import serializers
from .models import emprestimo
from datetime import datetime

class LoginSerializer(serializers.Serializer):
    imagem = serializers.ImageField(required = False)

class LoanSerializer(serializers.Serializer):
    valor = serializers.IntegerField(required=False)
    duracao = serializers.IntegerField(required=False)
    salario = serializers.IntegerField(required=False)
    profissao = serializers.CharField(max_length=255, required=False)
    documentos = serializers.ImageField(required=False)
    tiposempr = serializers.ChoiceField(choices=emprestimo.categories, required=False)
    estado = serializers.ChoiceField(choices=[("por resolver", "Por Resolver"), ("resolvido", "Resolvido")], default="por resolver")
    person = serializers.CharField(max_length=100, required=False)  
    
    # vi aqui: https://stackoverflow.com/questions/42904336/django-rest-framework-create-notimplementederror-when-making-http-post-req
    def create(self,validated_data):
        return emprestimo.objects.create(**validated_data)

class BankLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()