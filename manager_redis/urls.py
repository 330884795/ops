from django.urls import path

from . import views


app_name = 'cmdb'

urlpatterns = [
    path('', views.getredislist,name='getredislist'),

]