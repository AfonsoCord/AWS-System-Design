from django.db import models

class emprestimo(models.Model):
    user = models.CharField(max_length=100)
    categories = (("CHAB","Crédito Habitacional"),
                  ("CAUT","Crédito Automotivo"),
                  ("CEST","Crédito Estudantil"),
                  ("CPES","Crédito Pessoal"))
    valor = models.FloatField()
    duracao = models.PositiveIntegerField()
    salario = models.PositiveIntegerField(null=True)
    profissao = models.CharField(max_length=100)
    documentos = models.ImageField(upload_to="img",blank=True, null=True)
    tiposempr = models.CharField(max_length=100,choices=categories,blank= True)
    tempo = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=100)


    def __str__(self):

        return self.user