from django.urls import path

from . import views


app_name = 'monitor'

urlpatterns = [
    path('record/',views.jilu,name='jilu'),
    path('tmtest/',views.tmtest,name='tmtest'),
    path('slowuri/<hostname>',views.give_you_slow_uri,name='slowuri')
]