import requests
import sys

def auth(ip,port,user,password):
    # Define the headers of the authorization request
    headersToken = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    # Define the body of the authorization request
    data = '{"username":"'+user+'", "password":"'+password+'"}'

    protocol = "https"
    if str(ip) == 'localhost':
        protocol = 'http'

    # Perform the POST request to obtain X-Token Authorization
    try:
        response = requests.post(protocol+'://'+str(ip)+':'+str(port)+'/api/auth/login', headers=headersToken, data=data)
        X_AUTH_TOKEN = response.json()['token']
    except Exception as e:
        print("\nAn exception occurred while trying to obtain the authorization from SOURCE Thigsboard: ", e)
        sys.exit(1)

    return X_AUTH_TOKEN