import requests
import sys

def findDevice(devices, name):
    for d in devices:
        if d['name'] == name:
            return d

def getCustomerDevices(ip, port, X_AUTH_TOKEN, customerId):
    # Define the headers of the authorization request
    headers = {'Accept':'application/json','X-Authorization': 'Bearer '+X_AUTH_TOKEN}

    protocol = "https"
    if str(ip) == 'localhost':
        protocol = 'http'

    # Perform the GET request
    try:
        request = requests.get(protocol+"://"+str(ip)+":"+str(port)+"/api/customer/"+customerId+"/devices?pageSize=50&page=0",headers=headers)
        return request.json()['data']
    except Exception as e:
        print("\nAn exception occurred while trying to obtain the customer: ", e)
        sys.exit(1)
