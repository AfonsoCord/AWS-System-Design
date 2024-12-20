from django.db import models
from django.contrib.auth.models import User

class emprestimo(models.Model):
    categories = (("CHAB","Crédito Habitacional"),
                  ("CAUT","Crédito Automotivo"),
                  ("CEST","Crédito Estudantil"),
                  ("CPES","Crédito Pessoal"))
    valor = models.PositiveIntegerField()
    duracao = models.DateField()
    salario = models.PositiveIntegerField()
    profissao = models.CharField(max_length=100)
    documentos = models.ImageField(upload_to="img",blank=True, null=True)
    tiposempr = models.CharField(max_length=100,choices=categories,blank= True)
    tempo = models.DateTimeField(auto_now_add=True)
    person = models.ForeignKey(User, on_delete=models.CASCADE, related_name="emprestimo")
    estado = models.CharField(max_length=100)


    def __str__(self):
        return self.person