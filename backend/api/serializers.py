from rest_framework import serializers
from .models import emprestimo
from datetime import datetime

class LoginSerializer(serializers.Serializer):
    imagem = serializers.ImageField(required = False)

class LoanSerializer(serializers.Serializer):
    user = serializers.CharField()
    valor = serializers.IntegerField()
    duracao = serializers.IntegerField()
    salario = serializers.IntegerField()
    profissao = serializers.CharField(max_length=255)
    documentos = serializers.ImageField()
    tiposempr = serializers.ChoiceField(choices=emprestimo.categories)
    estado = serializers.ChoiceField(choices=[("por resolver", "Por Resolver"), ("resolvido", "Resolvido")], default="por resolver")
    
    # vi aqui: https://stackoverflow.com/questions/42904336/django-rest-framework-create-notimplementederror-when-making-http-post-req

class BankLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()