from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from .models import project
import jsonify

# Create your views here.
def index(request):
    return render(request, 'cmdb/css-bak.html')

def uv(request):
    return render(request,'cmdb/Uversion.html')

def getservicelist(request):
    print(request.GET)
    print(request.GET['service'])
    pro=project.objects.get(pro_name=request.GET['service'])
    ecs_list=[i.ip for i in pro.ecslist_set.all()]
    t={}
    t['data']=ecs_list
    #return HttpResponse('1.1.1.1')
    return JsonResponse(t)

def getprojectlist(request):
    a=[i.pro_name for i in project.objects.all()]
    t={}
    t['data']=a
    print(a)
    # return HttpResponse(jsonify(a))
    return JsonResponse(t)


