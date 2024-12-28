from django.db import models

# base de dados dos clientes
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
    documentos = models.ImageField(upload_to="img", blank=True, null=True)
    tiposempr = models.CharField(max_length=100, choices=categories, blank= True)
    tempo = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=100)
    creditscore = models.CharField(max_length=100, null=True, blank=True)
    decisao = models.CharField(max_length=100, null=True, blank=True)
    horario = models.CharField(max_length=100,null=True, blank=True)


    def __str__(self):

        return self.user
    
# base de dados dos horários de entrevista
class horario(models.Model):
    horario = models.CharField(max_length=100)
    id_emprestimo = models.PositiveIntegerField()
    cliente_selecionou = models.BooleanField(default=False)

    
    def __str__(self):

        return f"{self.horario}, empréstimo nº {str(self.id_emprestimo)}"