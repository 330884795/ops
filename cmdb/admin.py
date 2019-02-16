from django.contrib import admin
from . import models

# Register your models here.



class projectAdmin(admin.ModelAdmin):
    list_display = ('pro_name','pro_platform','pro_conf')

class ecslistAdmin(admin.ModelAdmin):
    list_display = ('ip','cpu','mem','project_name','platform')
    filter_horizontal=('ecs_project',)


admin.site.register(models.project,projectAdmin)
admin.site.register(models.ecslist,ecslistAdmin)