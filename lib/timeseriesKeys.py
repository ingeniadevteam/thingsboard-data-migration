import requests
import sys

def timeseriesKeys(ip, port, X_AUTH_TOKEN, Id, type):
    # Define the headers of the authorization request
    headers = {'Accept':'application/json','X-Authorization': 'Bearer '+X_AUTH_TOKEN}

    # Perform the GET request
    try:
        request = requests.get("https://"+str(ip)+":"+str(port)+"/api/plugins/telemetry/" + type + "/" + Id + "/keys/timeseries",headers=headers)
        return request.json()
    except Exception as e:
        print("\nAn exception occurred while trying to obtain the attributes: ", e)
        sys.exit(1)
