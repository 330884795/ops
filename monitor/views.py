from django.shortcuts import render
#from django.views.generic import
from .models import record
# Create your views here.


def jilu(request):
    a=record.objects.all().order_by('-date')
    return render(request,'monitor/Record.html',{'info':a})

def tmtest(request):
    return render(request,'monitor/test.html')
