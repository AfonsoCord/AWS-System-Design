from django.db import models
from django.contrib.auth.models import User

class emprestimo(models.Model):
    categories = (("CHAB","Crédito Habitacional"),
                  ("CAUT","Crédito Automotivo"),
                  ("CEST","Crédito Estudantil"),
                  ("CPES","Crédito Pessoal"))
    valor = models.PositiveIntegerField()
    duracao = models.PositiveIntegerField()
    salario = models.PositiveIntegerField()
    profissao = models.CharField(max_length=100)
    documentos = models.CharField(upload_to="img")
    tiposempr = models.CharField(choices=categories,blank= True)
    person = models.ForeignKey(User, on_delete=models.CASCADE, related_name="emprestimo")


    def __str__(self):
        return self.person