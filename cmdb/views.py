from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from .models import project,ecslist
import datetime
from queue import Queue

# Create your views here.
def index(request):
    return render(request, 'cmdb/css-bak.html')

def uv(request):
    return render(request,'cmdb/Uversion.html')

def testinfo(request):
    print(request.GET['service'],request.GET['action'])
    service = project.objects.get(pro_name=request.GET['service'])
    hosts_list = [i.ip for i in service.ecslist_set.all()]
    print(hosts_list)
    filetime = datetime.datetime.now().strftime('%H-%M-%S')
    with open(filetime+'-hosts','wt') as hostsfile:
        for i in hosts_list:
            hostsfile.write(i+' ansible_ssh_user=root ansible_ssh_pass="Vpcecs@2018!q@w#" ansible_ssh_port=22' + '\n')

    return HttpResponse('嘻嘻')

def getservicelist(request):
    print(request.GET)
    print(request.GET['service'])
    pro = project.objects.get(pro_name=request.GET['service'])
    ecs_list = [i.ip for i in pro.ecslist_set.all()]
    t={}
    t['data'] = ecs_list
    #return HttpResponse('1.1.1.1')
    return JsonResponse(t)

def getprojectlist(request):
    a = [i.pro_name for i in project.objects.all()]
    t = {}
    t['data'] = a
    print(a)
    # return HttpResponse(jsonify(a))
    return JsonResponse(t)


