from django.db import models
from django.contrib.auth.models import User


class Note(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notes")

    def __str__(self):
        return self.title
    

class emprestimo(models.Model):
    valor = models.PositiveIntegerField()
    duracao = models.PositiveIntegerField()
    salario = models.PositiveIntegerField()
    profissao = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    person = models.ForeignKey(User, on_delete=models.CASCADE, related_name="emprestimo")


    def __str__(self):
        return self.estado