import requests
import sys

def getRelations(ip, port, X_AUTH_TOKEN, fromId, fromType):
    # Define the headers of the authorization request
    headers = {'Accept':'application/json','X-Authorization': 'Bearer '+X_AUTH_TOKEN}

    protocol = "https"
    if str(ip) == 'localhost':
        protocol = 'http'

    # Perform the GET request
    try:
        request = requests.get(protocol+"://"+str(ip)+":"+str(port)+"/api/relations/info?fromId="+fromId+"&fromType="+fromType,headers=headers)
        return request.json()
    except Exception as e:
        print("\nAn exception occurred while trying to obtain the relations: ", e)
        sys.exit(1)

    return []