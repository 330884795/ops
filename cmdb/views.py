from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from .models import project,ecslist
from monitor.models import record
from .updateadhoc import newtasks
from pymongo import MongoClient
import threading
import datetime,time
import pika
import requests
from django.db.models import Q
from queue import Queue

rabbithost='172.22.0.69'
username='admin'
passwd='ablejava'
rabbitinfo=pika.PlainCredentials(username,passwd)

hostlist_queue=Queue(50)

uri = 'mongodb://ansible:ansible@dds-bp11e38d33b092a41.mongodb.rds.aliyuncs.com:3717/ansible'
client = MongoClient(uri)
db = client.ansible


def ConsumerCallback (channel, method, properties, body):
    # 将消息推入队列 (str(body,encoding = "utf8"))

    print(str(body,encoding = "utf-8"))
    print(type(str(body,encoding = "utf-8")))
    Service=eval(str(body,encoding = "utf-8"))
    get_host_info = project.objects.get(pro_name=Service['service'])
    if Service['action'] == 'update':
        ServiceList = [i.ip for i in get_host_info.ecslist_set.filter(~Q(platform='source'))]
    elif Service['action'] == 'reboot':
        ServiceList = [i.ip for i in get_host_info.ecslist_set.all()]
    #添加一个sql语句
    #db[service]=Service,在记录一个时间字段  方便后边线程更新 操作的记录.
    for i in ServiceList:
        hostlist_queue.put({'service_name':Service['service'],'hostfile':Service['file'],'host':i,'num':str(ServiceList.index(i)+1)+'-'+str(len(ServiceList)),'action':Service['action']})




class MyThread(threading.Thread):
    def run(self):
        while True:
            print('进入执行循环体')
            sigle = hostlist_queue.get()
            i, service, num, action, filename = sigle['host'], sigle['service_name'], sigle['num'], sigle['action'], \
                                                sigle['hostfile']
            project_info = project.objects.get(pro_name=sigle['service_name'])
            service_info=dict()
            service_info[service]=dict()
            service_info[service]['conf'] = project_info.pro_conf
            service_info[service]['rsync'] = project_info.pro_rsync
            service_info[service]['setup'] = project_info.pro_setup
            service_info[service]['url'] = project_info.pro_url.replace('ip:port',i+':'+project_info.pro_port)



            def screen():
                newtasks("/etc/ansible/nginx-hosts", "172.17.0.63",
                         "sed -i '/" + str(i) + "/s!^!#&!1' /usr/local/nginx/conf/conf.d/" + service_info[service][
                             'conf'])
                newtasks('/etc/ansible/nginx-hosts', '172.17.0.63', '/usr/local/nginx/sbin/nginx -s reload')
                newtasks('/etc/ansible/other-hosts', 'all', 'sh /root/shell/rsync-nginx.sh')
                thismoment = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                time.sleep(0.3)
                newtasks('/etc/ansible/other-hosts', '172.17.0.64',
                         'cat /usr/local/nginx/conf/conf.d/' + service_info[service]['conf'] + ' | grep ' + i)
                c = db.testnginx.find({'$and': [{"ip": '172.17.0.64'}, {"time": {"$gt": thismoment}}, ]})
                print(c)
                cc = c.next()
                print("check hosts:{}".format(cc))
                return cc
            def open_screen(output):
                if '#' in output['stdout']:
                    newtasks('/etc/ansible/nginx-hosts', '172.17.0.63',
                         "sed -i '/" + i + "/s!#!!1' /usr/local/nginx/conf/conf.d/" + service_info[service]['conf'])
                    newtasks('/etc/ansible/nginx-hosts', '172.17.0.63', '/usr/local/nginx/sbin/nginx -s reload')
                    print('打开文件注释')
                    newtasks('/etc/ansible/other-hosts', 'all', 'sh /root/shell/rsync-nginx.sh')

            def sync_version(i,filename,service,action):
                print(filename, i)  # 重启脚本
                print('sh '+service_info[service]['rsync'],'sh '+service_info[service]['setup']+' f-restart')
                if action == 'update':
                    print('更新服务')
                    newtasks(filename, i, 'sh '+service_info[service]['rsync'])
                print('重启服务前')
                newtasks(filename, i, 'nohup sh '+service_info[service]['setup']+' f-restart')
                print('重启服务后')

                for tt in range(20):
                    try:
                        print('请求检测url前')
                        if service_info[service].get('Action'):
                            r = requests.post(service_info[service]['url'], timeout=0.5)
                        else:
                            r = requests.get(service_info[service]['url'], timeout=0.5)
                        print('请求检测后 + 状态码:'+ str(r.status_code))
                        if r.status_code in [200,302]:
                            if service_info[service]['conf']:
                                newtasks('/etc/ansible/nginx-hosts', '172.17.0.63',
                                         "sed -i '/" + i + "/s!#!!1' /usr/local/nginx/conf/conf.d/" +
                                         service_info[service]['conf'])
                                newtasks('/etc/ansible/nginx-hosts', '172.17.0.63',
                                         '/usr/local/nginx/sbin/nginx -s reload')
                                print('打开文件注释')
                                newtasks('/etc/ansible/other-hosts', 'all', 'sh /root/shell/rsync-nginx.sh')
                            if action == 'update':
                                arecord=record(date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),user='update',cmd='succ',
                                               stdout=i+' '+num+' '+service)
                                arecord.save()
                            else:
                                arecord = record(date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                 user='reboot', cmd='succ',
                                                 stdout=i + ' ' + num + ' ' + service)
                                arecord.save()
                            print("服务判断启动成功")
                            break
                        elif tt == 19:
                            print('19次还没有成功')
                            if action == 'update':
                                arecord=record(date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),user='update',cmd='succ',
                                               stdout=i+' '+num+' '+service+' 服务启动失败')
                                arecord.save()
                            else:
                                arecord = record(date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                 user='reboot', cmd='succ',
                                                 stdout=i + ' ' + num + ' ' + service+' 服务启动失败')
                    except:
                        print('调用服务失败,等待7秒后发起下一次调用')
                        time.sleep(7)

            if service_info[service]['conf']:
                info = screen()
                print('有配置文件')
                if '#' in info['stdout']:
                    print('检测注释是否成功')
                    sync_version(i,filename,service,action)
                else:
                    if action == 'update':
                        arecord = record(date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                     user='update', cmd='failed',
                                     stdout=i + ' ' + num + ' ' + service+' 配置文件注释失败')
                        arecord.save()
                    else:
                        arecord = record(date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                         user='reboot', cmd='succ',
                                         stdout=i + ' ' + num + ' ' + service+' 配置文件注释失败')
                        arecord.save()
                    print('注释有问题')
            else:
                print("无配置文件")
                sync_version(i,filename,service,action)




            print(service_info)



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
    filetime = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    with open(filetime+'-hosts','wt') as hostsfile:
        for i in hosts_list:
            hostsfile.write(i+' ansible_ssh_user=root ansible_ssh_pass="Vpcecs@2018!q@w#" ansible_ssh_port=22' + '\n')

    mqinfo = "{'service':" + "'" + str(request.GET['service']) + "'" + ",'action':" + "'" + str(
        request.GET['action']) + "'" + ",'file':" + "'" + str(filetime + '-hosts') + "'}"
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbithost, credentials=rabbitinfo))
    channel = connection.channel()
    channel.queue_declare(queue='yunwei-uV', durable=True)
    channel.basic_publish(exchange='', routing_key='yunwei-uV', body=mqinfo)
    print('消息发送到rabbit:{}'.format(mqinfo))
    connection.close()
    if request.GET['action'] == 'update':
        arecord = record(date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user='用户', cmd='提交更新服务:'+request.GET['service'],stdout='请求后端已经在处理.')
        arecord.save()
    else:
        arecord = record(date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user='用户',
                         cmd='提交重启服务:' + request.GET['service'], stdout='请求后端已经在处理.')
        arecord.save()


    return HttpResponse('嘻嘻')

def rabbit1(request):
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbithost, credentials=rabbitinfo))
    channel = connection.channel()
    channel.queue_declare(queue='yunwei-uV', durable=True)
    channel.basic_consume(ConsumerCallback, queue='yunwei-uV', no_ack=True)
    print("i'm rabbit-1")
    print('start')

    for i in range(1):
        c = MyThread()
        c.start()

    channel.start_consuming()


def getservicelist(request):
    print(request.GET)
    print(request.GET['service'])
    pro = project.objects.get(pro_name=request.GET['service'])
    if request.GET['action'] == 'update':
        ecs_list = [i.ip for i in pro.ecslist_set.filter(~Q(platform='source'))]
    else:
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


