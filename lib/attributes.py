import requests
import sys
import json

def findAttribute(attributes, attribute):
    for a in attributes:
        if a['key'] == attribute:
            return a

def getAttributeKeys(ip, port, X_AUTH_TOKEN, deviceId, scope):
    # Define the headers of the authorization request
    headers = {'Accept':'application/json','X-Authorization': 'Bearer '+X_AUTH_TOKEN}

    protocol = "https"
    if str(ip) == 'localhost':
        protocol = 'http'
    # Perform the GET request
    try:
        request = requests.get(protocol+"://"+str(ip)+":"+str(port)+"/api/plugins/telemetry/DEVICE/"+deviceId+"/keys/attributes/"+scope,headers=headers)
        return request.json()
        
    except Exception as e:
        print("\nAn exception occurred while trying to obtain the attributes: ", e)
        sys.exit(1)


def getAttributes(ip, port, X_AUTH_TOKEN, deviceId):
    # Define the headers of the authorization request
    headers = {'Accept':'application/json','X-Authorization': 'Bearer '+X_AUTH_TOKEN}

    # Perform the GET request
    try:
        request = requests.get("https://"+str(ip)+":"+str(port)+"/api/plugins/telemetry/DEVICE/"+deviceId+"/values/attributes",headers=headers)
        return request.json()
        
    except Exception as e:
        print("\nAn exception occurred while trying to obtain the attributes: ", e)
        sys.exit(1)


def postServerAttributes(ip, port, X_AUTH_TOKEN, deviceId, data):
    # Define the headers of the authorization request
    headers = {'Accept':'application/json','X-Authorization': 'Bearer '+X_AUTH_TOKEN,"Content-Type": "application/json"}

    # Perform the POST request
    try:
        requests.post("https://"+str(ip)+":"+str(port)+"/api/plugins/telemetry/"+deviceId+"/SERVER_SCOPE",json=data,headers=headers)
        
    except Exception as e:
        print("\nAn exception occurred while trying to post the attributes: ", e)
        sys.exit(1)