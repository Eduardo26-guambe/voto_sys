from django.db import models

# Create your models here.
class chefe(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class votos(models.Model):
    chefe = models.ForeignKey(chefe, on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, unique=True)
    data_voto = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Voto de {self.user.username} para {self.chefe.nome}"