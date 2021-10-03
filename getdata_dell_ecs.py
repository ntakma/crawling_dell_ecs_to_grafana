import requests
import json
from requests.api import head
from requests.sessions import session
import urllib3
from datetime import datetime, time

requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
try:
    requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
except AttributeError:
    # no pyopenssl support used / needed / available
    pass
URL_DELL_ECS = "IP-SERVER"
Authorization = "Authorizon-KEY"
def open_session():
    url = URL_DELL_ECS+'login'
    header = {
        'Prefer': URL_DELL_ECS,
        'Accept':'application/json, text/plain, */*',
        'Origin': URL_DELL_ECS,
        'Authorization': Authorization,
        'Cookie': 'ECSAuthToken=; XSRF-TOKEN=; ECSUI_SESSION='
    }
    resp = requests.get(url, headers=header, verify=False)
    text_resp = json.loads(resp.text)
    # print(resp)
    if text_resp.get('status') == 'success':
        datacookie= resp.cookies.get_dict()
        Ecs_autoken= datacookie.get('ECSAuthToken')
        xsrf_token = datacookie.get('XSRF-TOKEN')
        return Ecs_autoken, xsrf_token

def get_alert():
    Ecs_autoken, xsrf_token = open_session()
    link = URL_DELL_ECS+'dashboard/link'
    header = {
        'X-SDS-AUTH-TOKEN':Ecs_autoken,
        'Origin': URL_DELL_ECS,
        'cookie': 'XSRF-TOKEN='+ xsrf_token+'; GsGuideLastState=dismissed; GsGuideStep=buckets; ECSAuthToken='+Ecs_autoken,
        'Referer':URL_DELL_ECS,
        'Accept':'application/json, text/plain, */*',
        'Content-Type':'application/json;charset=utf-8'
    }
    ### get time query 12AM today to 12AM tomorow. default query
    today = int(datetime.combine(datetime.today(),time()).timestamp())    
    startday = str(today)
    enday = str(today+86400)
    request_payload = '/dashboard/zones/localzone?dataType=current&dataType=historical&startTime='+startday+'&endTime='+enday+'&interval=300'

    resp = requests.post(link,data=request_payload, headers=header, verify=False)
    data  = json.loads(resp.text)
    # all result return for request.
    result = data.get('data')
#    get alert 
    if data.get('isSuccess') is True:
        #get node:
        some_param = {
        'numNodes' : int(result.get('numNodes')),
        'numGoodNodes' : int(result.get('numGoodNodes')),
        'numBadNodes' : int(result.get('numBadNodes')),
        # get disk 
        'numDisks' : int(result.get('numDisks')),
        'numGoodDisks' : int(result.get('numGoodDisks')),
        'numBadDisks' : int(result.get('numBadDisks')),
        #get space 
        'diskSpaceTotalCurrent' : int(result.get('diskSpaceTotalCurrent')[0].get('Space'))/1073741824, #caculate on log(1024)
        'diskSpaceFreeCurrent' : int(result.get('diskSpaceFreeCurrent')[0].get('Space'))/1073741824,
        'diskSpaceAllocatedCurrent' : int(result.get('diskSpaceAllocatedCurrent')[0].get('Space'))/1073741824,
        #get alert
        'alertsNumUnackError': int(result.get('alertsNumUnackError')[0].get('Count')),
        'alertsNumUnackCritical': int(result.get('alertsNumUnackCritical')[0].get('Count'))
        }
        return some_param
    if data.get('isSuccess') is False:
        return 
def to_influx():
    dict1 = get_alert()
    output = "{} ".format("ecs_emc")
    for key in dict1.keys():
        output = output + "{}={},".format(key, int(dict1[key]))
    output = output[:-1]
    return output

if __name__ == '__main__':
    print(to_influx())
