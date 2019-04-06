import requests
import datetime
import json
import requests
from requests_html import HTML
import smtplib
import redis
from .models import urlinfo
from influxdb import InfluxDBClient
from email.header import Header
from email.mime.text import MIMEText
from concurrent import futures

import rdbtools
import elasticsearch
mail_list = ['wangyue2@able-elec.com','jikaiyuan@able-elec.com','huangming@able-elec.com','chenzhiyuan@able-elec.com','guozengcheng@able-elec.com','chenyongbin@able-elec.com','wuchuan@able-elec.com','zhangying445@163.com']
#mail_list = ['wangyue2@able-elec.com','330884795@qq.com']
#mail_list = ['wangyue2@able-elec.com']


cache=redis.StrictRedis(host='r-bp18e46a96212534.redis.rds.aliyuncs.com', port=6379, password='Uccvod12345', db=0)



def test():
    print('testone')


def insert_influxdb(project,manager,url,urldesc,data,code,rtime):
    client = InfluxDBClient(host='172.22.0.75', port=8086, database='urlmonitor',username='', password='',)
    j=[{"measurement": "urlinfo","tags": {"tags":"tt","pproject":project,},"fields": {"project":project,"manager":manager,"url":url,'urldesc':urldesc,"respone_data":data,"respone_code":code,"rtime":rtime}}]
    client.write_points(j)


def monitor_url():
    s = smtplib.SMTP_SSL('smtp.exmail.qq.com', 465)
    s.login('service8@zhihuishu.com', 'able1314')
    a=urlinfo.objects.all()
    for i in a:
        try:
            #r=requests.get(i.url,timeout=2)
            r = requests.get(i.url,timeout=2)
            rtime=r.elapsed.total_seconds()#秒
            #print(i.url,rtime)
            if r.status_code in [200,302]:
                insert_influxdb(i.project,i.manager,i.url,i.urlinfo,r.text[:100],r.status_code,rtime)
            else:
                msg = MIMEText('调用uri:'+r.url+' '+','+'接口描述:'+i.urlinfo+',返回数据:'+r.text+',status:'+str(r.status_code)+',负责人:'+i.manager)
                msg['Subject'] = "监控{}项目接口-失败状态".format(i.project)
                msg['From'] = 'service8@zhihuishu.com'
                msg['To'] = ','.join(mail_list)
                s.sendmail('service8@zhihuishu.com',mail_list,msg.as_string())
                insert_influxdb(i.project, i.manager, i.url, i.urlinfo, r.text[:100], r.status_code,r.elapsed.microseconds/(1000*1000))
                #print('链接有问题,将给大家发送邮件.')
        except:
            msg = MIMEText('调用uri:' + i.url+ ',接口描述:' + i.urlinfo+ ',status:' + '访问异常 ,负责人:' + i.manager)
            msg['Subject'] = "监控{}项目接口-访问超时状态".format(i.project)
            msg['From'] = 'service8@zhihuishu.com'
            msg['To'] = ','.join(mail_list)
            s.sendmail('service8@zhihuishu.com', mail_list, msg.as_string())
            #print('链接有问题,将给大家发送邮件.')
            #print(i.url)
            #print('有问题的url')


# def dubbo_mon():
#     r = requests.get('http://172.22.0.65:8080/services.html', timeout=2)
#     html = HTML(html=r.text)
#     tbody = html.find('tbody')[1]
#     tr = tbody.find('tr')
#     problem = []
#     for i in tr:
#         service = i.text.split('\n')[0]
#         # print(service)
#         try:
#             rr = requests.get('http://172.22.0.65:8080/statistics.html?service=' + service, timeout=10)
#         except Exception as e:
#             #print(e)
#             #print(service + '--has problem')
#             #problem.append(service)
#             pass
#         html1 = HTML(html=rr.text)
#         if len(html1.find('tbody')) >= 2:
#             tbody1 = html1.find('tbody')[1]
#             tr1 = tbody1.find('tr')
#             # print(tbody1.text)
#             total = 0
#             for l in tr1:
#                 total += int(l.find('td')[2].text.split('-->')[0]) + int(l.find('td')[2].text.split('-->')[1])
#             else:
#                 #info=cache.get(service).decode()
#                 if cache.get(service):
#                     if total != 0:
#                         #print(service,total,cache.get(service).decode())
#                         if total - int(cache.get(service).decode()) > 200:
#                         #print('每5分钟失败100次')
#                             if service == 'com.zhihuishu.qa.openapi.qaweb.QaWebQuestionOpenService':
#                                 cache.set(service, total)
#                             else:
#                                 problem.append({'name':service,'5分钟前失败次数':cache.get(service).decode(),'现在失败次数:':str(total)})
#                                 cache.set(service, total)
#                         else:
#                             cache.set(service, total)
#                 else:
#                     cache.set(service, total)
#                 #print(service, total)
#     else:
#         # print('=============================')
#         # print('=============================')
#         # print('=============================')
#         if len(problem) > 0:
#             s = smtplib.SMTP_SSL('smtp.exmail.qq.com', 465)
#             s.login('service8@zhihuishu.com', 'able1314')
#             msg = MIMEText(str(problem))
#             msg['Subject'] = "监控dubbo接口失败状态-5分钟失败超过200次"
#             msg['From']='service8@zhihuishu.com'
#             msg['To']=','.join(mail_list)
#             s.sendmail('service8@zhihuishu.com', mail_list, msg.as_string())
        # print(problem)


def return_service_list():
    r = requests.get('http://172.22.0.65:8080/services.html', timeout=2)
    html = HTML(html=r.text)
    tbody = html.find('tbody')[1]
    tr = tbody.find('tr')
    trd = [i.text.split('\n')[0] for i in tr]
    #print(trd)
    trd.remove('com.zhihuishu.qa.openapi.qaweb.QaWebQuestionOpenService')
    return trd

def check_num(service):
    try:
        rr = requests.get('http://172.22.0.65:8080/statistics.html?service=' + service,timeout=10)
    except Exception as e:
        print(e,service)
        rr = False
    if rr:
        html1 = HTML(html=rr.text)
        if len(html1.find('tbody')) >= 2:
            tbody1 = html1.find('tbody')[1]
            tr1 = tbody1.find('tr')
            total = 0
            for l in tr1:
                total += int(l.find('td')[2].text.split('-->')[0]) + int(l.find('td')[2].text.split('-->')[1])
            else:
                #print('接口名字:{},失败次数:{}'.format(service,total))
                if cache.get(service):
                    if total != 0:
                        if total - int(cache.get(service).decode()) > 200:
                            #problem.append({'name':service,'5分钟前失败次数':cache.get(service).decode(),'现在失败次数:':str(total)})
                            num=cache.get(service).decode()
                            cache.set(service, total)
                            print(num,total,service)
                            print({'name':service,'5分钟前失败次数':num,'现在失败次数:':str(total)})
                            return {'name':service,'5分钟前失败次数':num,'现在失败次数:':str(total)}
                        else:
                            cache.set(service, total)
                    else:
                        cache.set(service, 0)
                else:
                    cache.set(service, total)


def dubbo_mon():
    with futures.ThreadPoolExecutor(20) as ex:
        res = ex.map(check_num, return_service_list())

    comment = list(res)
    # comment.remove('com.zhihuishu.qa.openapi.qaweb.QaWebQuestionOpenService')
    for i in range(comment.count(None)):
        comment.remove(None)

    if len(comment) > 0:
        s = smtplib.SMTP_SSL('smtp.exmail.qq.com', 465)
        s.login('service8@zhihuishu.com', 'able1314')
        msg = MIMEText(str(comment))
        msg['Subject'] = "监控dubbo接口失败状态-5分钟失败超过200次"
        msg['From'] = 'service8@zhihuishu.com'
        msg['To'] = ','.join(mail_list)
        print('send mail before')
        s.sendmail('service8@zhihuishu.com',mail_list, msg.as_string())

# print(r.url,r.text[:100],r.status_code)


def slow_url():
    req_data = {  "size": 3,
  "query": {
    "term": {
      "hostname.keyword": "online.zhihuishu.com"
      }
    },
    "aggs": {
      "myaggs": {
        "range": {
          "field": "timestamp",
          "ranges": [
            {
              "from": "now-10m",
              "to": "now"
            }
          ]
        },
        "aggs": {
          "avgreq": {
            "avg": {
              "field": "request_time"
            }
          }
        }
        }
      }
    }





