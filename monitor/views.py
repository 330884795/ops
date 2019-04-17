from django.shortcuts import render
from django.http import HttpResponse
#from django.views.generic import
from .models import record
# Create your views here.
import datetime
import requests
import json


def jilu(request):
    a=record.objects.all().order_by('-date')
    return render(request,'monitor/Record.html',{'info':a})

def tmtest(request):
    return render(request,'monitor/test.html')

def give_you_slow_uri(request,hostname):
        now = datetime.datetime.now()
        aday = datetime.timedelta(days=1)
        yesterday = (now - aday).strftime('%Y.%m.%d')
        headers = {'Content-Type': 'application/json'}
        info = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {
                            "hostname": hostname
                        }}
                    ],
                    "must_not": [
                        {"match": {
                            "requestUri": "/aidedteaching/file/downloadFile"
                        }}
                    ]
                }
            },
            "sort": [
                {
                    "request_time": {
                        "order": "desc"
                    }
                }
            ],
            "_source": ["requestUri", "request_time"]
            , "size": 10
        }
        sub_data = json.dumps(info)
        r = requests.post('http://172.19.103.161:9200/nginx_access-' + yesterday + '/doc/_search?', headers=headers,
                          data=sub_data)
        #print(r.json())
        respone_data = [str(i['_source']['request_time']) + 's :' + i['_source']['requestUri']+'<br>' for i in r.json()['hits']['hits']]

        return HttpResponse(respone_data)

