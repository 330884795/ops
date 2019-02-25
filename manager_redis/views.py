from django.shortcuts import render
import redis
from .models import redismessage
from django.forms import ModelChoiceField
# Create your views here.
def getredislist(request):
    hosts = redismessage.objects.values_list('host',flat=True)
    ip=request.POST.get('host')
    print(ip)
    passw=chamima(ip)
    command=request.POST.get('command')
    print(command)
    key=request.POST.get('key')
    value=request.POST.get('value')
    conn = redis.Redis(host=ip, port=6379,password=passw,decode_responses=True)
    jieguo='redis叉叉叉'
    try:
        if command == 'get':
            jieguo=conn.get(key)
        elif command == 'set':
            conn.set(key,value)
            if conn.get(key):
                jieguo='新增成功'
        elif command == 'del':
            if conn.delete(key):
                jieguo='已删除'
            else:
                jieguo='无此key'
        elif command == 'hgetall':
            jieguo=conn.hgetall(key)
        elif command == 'sadd':
            conn.sadd(key,value)
            if conn.smembers(key):
                jieguo='新增成功'
            else:
                jieguo='请检查'
        elif command=='smembers':
            conn.smembers(key)
        elif command=='hmset':
            value=eval(value)
            conn.hmset(key,value)
            if conn.hgetall(key):
                jieguo="bingo"
        elif command=='lpush':
            conn.lpush(key,value)
            if conn.lrange(key,1,2):
                jieguo="bingo"
        elif command == 'lrange':
            k=key.split()
            print(k[0],k[1],k[2])
            jieguo=conn.lrange(k[0],int(k[1]),int(k[2]))
        elif command=='zadd':
            conn.zadd(key,value)
            if conn.zrange(key,1,2):
                jieguo="bingo"
        elif command=='zrange':
            k = key.split()
            print(k[0], k[1], k[2])
            jieguo=conn.zrange(k[0],int(k[1]),int(k[2]))
    except Exception  as error:
        print (error)

        return render(request, 'manager_redis/error.html',{'error':error})
    else:
    #print(jieguo)
        return  render(request,'manager_redis/manager_redis.html',{'hosts': hosts,'jieguo':jieguo})
def chamima(host):
    if host == None:
        ip='localhost'
        return ip
    else:
        print(host)
        p=redismessage.objects.values('password').get(host=host)
        passw=p.get('password')
        print(passw)
        return passw
def test(request,jieguo):
    pass
    return render(request, 'manager_redis/test.html',{'jieguo': jieguo})
