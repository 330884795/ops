from django.urls import path

from . import views


app_name = 'manager_redis'

urlpatterns = [
    path('', views.getredislist,name='getredislist'),
    path('error.html/',views.test)

]