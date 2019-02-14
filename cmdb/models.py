from django.db import models

# Create your models here.


class project(models.Model):
    pro_name = models.CharField(max_length=20,)
    pro_platform = models.CharField(max_length=20,null=True,blank=True)
    pro_conf = models.CharField(max_length=100,null=True,blank=True)
    pro_url = models.CharField(max_length=200)
    pro_rsync = models.CharField(max_length=200)
    pro_setup = models.CharField(max_length=200)
    pro_software = models.CharField(max_length=100,null=True,blank=True)
    pro_port = models.CharField(max_length=20)
    pro_action = models.CharField(max_length=20,null=True,blank=True)


    def __str__(self):
        return self.pro_name


class ecslist(models.Model):
    ip = models.CharField(max_length=70)
    cpu = models.CharField(max_length=10)
    mem = models.CharField(max_length=10)
    inst_id = models.CharField(max_length=20,null=True,blank=True)
    platform = models.CharField(max_length=20,null=True,blank=True)
    ecs_project = models.ManyToManyField(project)

    def __str__(self):
        return self.ip

    def project_name(self):
        return "\n".join([p.pro_name for p in self.ecs_project.all()])