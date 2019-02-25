from django.contrib import admin
from . import models
# Register your models here.

class redismessageAdmin(admin.ModelAdmin):
    list_display = ('host','password')

admin.site.register(models.redismessage,redismessageAdmin)