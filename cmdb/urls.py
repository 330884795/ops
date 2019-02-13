from django.urls import path

from . import views


urlpatterns = [
    path('', views.index,name='index'),
    path('update/', views.uv,name='uv'),
    path('getservicelist/',views.getservicelist,name='getservicelist'),
    path('getprojectlist/',views.getprojectlist,name='getprojectlist'),
    path('testinfo/',views.testinfo,name='testinfo'),
]