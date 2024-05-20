import requests
import sys

def getDeviceCredentials(ip, port, X_AUTH_TOKEN, deviceId):
    # Define the headers of the authorization request
    headers = {'Accept':'application/json','X-Authorization': 'Bearer '+X_AUTH_TOKEN}

    protocol = "https"
    if str(ip) == 'localhost':
        protocol = 'http'

    # Perform the GET request
    try:
        request = requests.get(protocol+"://"+str(ip)+":"+str(port)+"/api/device/"+deviceId+"/credentials",headers=headers)
        return request.json()
    except Exception as e:
        print("\nAn exception occurred while trying to obtain the relations: ", e)
        sys.exit(1)

    return []