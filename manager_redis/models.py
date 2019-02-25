from django.db import models

# Create your models here.
class redismessage(models.Model):
    host = models.CharField(max_length=200)
    password = models.CharField(max_length=200,default="")


def __str__(self):
    return self.host