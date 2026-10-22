from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Feedback(models.Model):
    REACTION_CHOICES = (
        ('like', '👍'),
        ('love', '❤️'),
        ('thanks', '🙏'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='feedbacks',
    )
    message = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    reaction = models.CharField(
        max_length=10,
        choices=REACTION_CHOICES,
        blank=True,
        default='',
    )

    class Meta:
        ordering = ('created_at', 'pk')

    def __str__(self):
        return f'Feedback de {self.user}: {self.message[:50]}'


#Tabela presidente
class pres(models.Model):
    nome =models.CharField(null=False, max_length=100)
    foto =models.CharField(null=False, max_length=250)
    descricao =models.CharField(null=False, max_length=255)
    propostas =models.CharField(null=False, max_length=255)

    def __str__(self):
        return self.nome

#Tabela secretaria
class sec(models.Model):
    nome =models.CharField(null=False, max_length=100)
    foto =models.CharField(null=False, max_length=250)
    descricao =models.CharField(null=False, max_length=255)
    propostas =models.CharField(null=False, max_length=255)

    def __str__(self):
        return self.nome

#Tabela estaticista
class est(models.Model):
    nome =models.CharField(null=False, max_length=100)
    foto =models.CharField(null=False, max_length=250)
    descricao =models.CharField(null=False, max_length=255)
    propostas =models.CharField(null=False, max_length=255)

    def __str__(self):
        return self.nome
#Tabela de voto presidente
class p_votos(models.Model):
    p_id= models.ForeignKey(pres, on_delete=models.CASCADE)
    user_id= models.OneToOneField(User, on_delete=models.CASCADE, unique=True)

    def __str__(self):
        return f"voto de {self.user_id} para o {self.p_id}"

#Tabela de voto secretaria
class s_votos(models.Model):
    s_id= models.ForeignKey(sec, on_delete=models.CASCADE)
    user_id= models.OneToOneField(User, on_delete=models.CASCADE, unique=True)

    def __str__(self):
        return f"voto de {self.user_id} para o {self.s_id}"

#Tabela de voto estaticista
class e_votos(models.Model):
    e_id= models.ForeignKey(est, on_delete=models.CASCADE)
    user_id= models.OneToOneField(User, on_delete=models.CASCADE, unique=True)

    def __str__(self):
        return f"voto de {self.user_id} para o {self.e_id}"
