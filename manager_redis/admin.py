from django.contrib import admin
from . import models
# Register your models here.

class redismessageAdmin(admin.ModelAdmin):
    list_display = ('host','password','users')

admin.site.register(models.redismessage,redismessageAdmin)