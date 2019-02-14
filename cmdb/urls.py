from django.urls import path

from . import views


app_name = 'cmdb'

urlpatterns = [
    path('', views.index,name='index'),
    path('update/', views.uv,name='uv'),
    path('getservicelist/',views.getservicelist,name='getservicelist'),
    path('getprojectlist/',views.getprojectlist,name='getprojectlist'),
    path('testinfo/',views.testinfo,name='testinfo'),
    path('rabbit1/',views.rabbit1,name='rabbit1'),
]