from rest_framework import serializers
from .models import emprestimo

class LoginSerializer(serializers.Serializer):
    imagem = serializers.ImageField(required=False)

class LoanSerializer(serializers.Serializer):
    user = serializers.CharField(required=False)
    valor = serializers.FloatField()
    duracao = serializers.IntegerField()
    salario = serializers.IntegerField(required=False)
    profissao = serializers.CharField(max_length=255, required=False)
    documentos = serializers.ImageField(required=False)
    tiposempr = serializers.ChoiceField(choices=emprestimo.categories, required=False)
    estado = serializers.ChoiceField(choices=[("por resolver", "Por Resolver"),
                                              ("pendente", "Pendente"),
                                              ("resolvido", "Resolvido")], default="por resolver")
    
    # vi aqui: https://stackoverflow.com/questions/42904336/django-rest-framework-create-notimplementederror-when-making-http-post-req

class BankLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()