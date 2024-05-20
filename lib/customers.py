import requests
import sys

def findCustomer(customers, customer):
    for c in customers:
        if c['name'] == customer:
            return c['id']['id']

def getCustomer(customers, customer):
    for c in customers:
        if c['name'] == customer:
            return c

def getCustomers(ip, port, X_AUTH_TOKEN):
    # Define the headers of the authorization request
    headers = {'Accept':'application/json','X-Authorization': 'Bearer '+X_AUTH_TOKEN}

    protocol = "https"
    if str(ip) == 'localhost':
        protocol = 'http'

    # Perform the GET request
    try:
        request = requests.get(protocol+"://"+str(ip)+":"+str(port)+"/api/customers?pageSize=50&page=0",headers=headers)
        return request.json()['data']
    except Exception as e:
        print("\nAn exception occurred while trying to obtain the customer: ", e)
        sys.exit(1)


def getCustomerAssets(ip, port, X_AUTH_TOKEN, customerId):
    # Define the headers of the authorization request
    headers = {'Accept':'application/json','X-Authorization': 'Bearer '+X_AUTH_TOKEN}
    
    protocol = "https"
    if str(ip) == 'localhost':
        protocol = 'http'

    # Perform the GET request
    try:
        request = requests.get(protocol+"://"+str(ip)+":"+str(port)+"/api/customer/"+customerId+"/assets?pageSize=50&page=0",headers=headers)
        return request.json()['data']
    except Exception as e:
        print("\nAn exception occurred while trying to obtain the customer: ", e)
        sys.exit(1)
