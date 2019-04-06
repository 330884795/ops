import requests
import datetime
import json





def requests_time(hostname):
    now = datetime.datetime.now().strftime('%Y.%m.%d')
    all_req_data={  "size": 3,
        "query": {
        "match_all": {}
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
    alone_req_data={ "size": 1,
  "query": {
    "match": {
      "hostname": hostname
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
    if hostname == 'all':
        sub_data = json.dumps(all_req_data)
    else:
        sub_data = json.dumps(alone_req_data)


    headers = {'Content-Type': 'application/json'}
    r=requests.post('http://172.19.103.161:9200/nginx_access-'+now+'/doc/_search?',headers=headers,data=sub_data)

    req_time=r.json()['aggregations']['myaggs']['buckets'][0]['avgreq']['value']
    req_from_time = r.json()['aggregations']['myaggs']['buckets'][0]['from_as_string']
    req_to_time = r.json()['aggregations']['myaggs']['buckets'][0]['to_as_string']

    if req_time > 1:
        print(req_time,req_from_time,req_to_time)




def slow_uri():
    now = datetime.datetime.now().strftime('%Y.%m.%d')
    headers = {'Content-Type': 'application/json'}
    req_data={ "size": 0,
  "query": {
    "bool": {
      "must_not": [
        {"match": {
          "requestUri": "/zhserp/fileResource/fileDownload/*"
        }},
        {"match": {
          "requestUri": "/able-commons//upload/receiver"
        }}
      ]
    }
  },
  "aggs":{
    "testaggs":{
      "top_hits": {
        "size": 20,
        "_source": {"includes": ["requestUri","request_time"]}
        , "sort": [{"request_time": {"order": "desc"}}]

      }
    }
  }
}
    sub_data = json.dumps(req_data)
    r = requests.post('http://172.19.103.161:9200/nginx_access-' + now + '/doc/_search?', headers=headers,
                      data=sub_data)

    respone_data = r.json()['aggregations']['testaggs']['hits']['hits']
    split_date = [{i["_source"]["requestUri"]:i["_source"]["request_time"]}for i in respone_data]
    print(split_date)

