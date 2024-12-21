from django.db import models
import uuid

class emprestimo(models.Model):
    id = models.UUIDField(primary_key=True, max_length=100, default='default_id', unique=True)
    categories = (("CHAB","Crédito Habitacional"),
                  ("CAUT","Crédito Automotivo"),
                  ("CEST","Crédito Estudantil"),
                  ("CPES","Crédito Pessoal"))
    valor = models.PositiveIntegerField()
    duracao = models.PositiveIntegerField()
    salario = models.PositiveIntegerField(null=True)
    profissao = models.CharField(max_length=100)
    documentos = models.ImageField(upload_to="img",blank=True, null=True)
    tiposempr = models.CharField(max_length=100,choices=categories,blank= True)
    tempo = models.DateTimeField(auto_now_add=True)
    person = models.CharField(max_length=100, null=True)
    estado = models.CharField(max_length=100)


    def __str__(self):

        return self.person