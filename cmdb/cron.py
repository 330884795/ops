from .models import urlinfo
import requests

def test():
    print('testone')


def monitor_url():
    a=urlinfo.objects.all()
    for i in a:
        r=requests.get(i.url)
        print(r.url,r.text[:100],r.status_code)






