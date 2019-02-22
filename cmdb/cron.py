import requests
import datetime
import json
import requests
import smtplib
from .models import urlinfo
from influxdb import InfluxDBClient
from email.header import Header
from email.mime.text import MIMEText
mail_list = ['wangyue2@able-elec.com']
s=smtplib.SMTP_SSL('smtp.exmail.qq.com',465)
s.login('service8@zhihuishu.com','able1314')

def test():
    print('testone')


def insert_influxdb(project,manager,url,urldesc,data,code,rtime):
    client = InfluxDBClient(host='172.22.0.75', port=8086, database='urlmonitor',username='', password='',)
    j=[{"measurement": "urlinfo","tags": {"tags":"tt","pproject":project,},"fields": {"project":project,"manager":manager,"url":url,'urldesc':urldesc,"respone_data":data,"respone_code":code,"rtime":rtime}}]
    client.write_points(j)


def monitor_url():
    a=urlinfo.objects.all()
    for i in a:
        r=requests.get(i.url)
        rtime=r.elapsed.total_seconds()#秒
        print(rtime)
        if r.status_code in [200,302]:
            insert_influxdb(i.project,i.manager,i.url,i.urlinfo,r.text[:100],r.status_code,rtime)
        else:
            msg = MIMEText('调用uri:'+r.url,',接口描述:'+i.urlinfo,',返回数据:'+r.text,',status:'+str(r.status_code),',负责人:'+i.manager)
            msg['Subject'] = "监控{}项目接口-失败状态".format(i.project)
            s.sendmail('service8@zhihuishu.com',mail_list,msg.as_string())
            insert_influxdb(i.project, i.manager, i.url, i.urlinfo, r.text[:100], r.status_code,r.elapsed.microseconds/(1000*1000))
            print('链接有问题,将给大家发送邮件.')









# print(r.url,r.text[:100],r.status_code)






