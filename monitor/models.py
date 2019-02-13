from django.db import models

# Create your models here.
class record(models.Model):
    date = models.CharField(max_length=20,)
    user = models.CharField(max_length=20)
    cmd = models.CharField(max_length=100)
    stdout = models.CharField(max_length=200)

    def __str__(self):
        return self.date