import requests
import logging
import paho.mqtt.client as mqtt
import time
from tqdm import tqdm
import json

from lib.auth import auth

'''
@Name getData(ip,port,user,password,deviceId,key,startTs,endTs)
@Return Returns a timeseries with the response to the HTTP RESTful request
@Parameters
    ip: ip address of target ThingsBoard
    port: port used by the target ThingsBoard
    token: authorization token
    deviceId: id of the device to read
    key: key of the timeseries to read
    startTs: first unix timestamp to fetch
    endTs: last unix timestamp to fetch
@Notes The function reads all the database entries associated with the device and key, with a LIMIT of 200000 and no aggregation
'''
def getData(ip,port,X_AUTH_TOKEN,deviceId,key,startTs,endTs,type="DEVICE"):
 
    # Define some constants 
    INTERVAL = '0'
    LIMIT = '200000'
    AGG = 'NONE'    

    # Define the headers of the request
    headers = {'Accept':'application/json','X-Authorization': 'Bearer '+X_AUTH_TOKEN}

    # Perform the GET request to obtain timeseries
    try:
        r = requests.get("https://"+str(ip)+":"+str(port)+"/api/plugins/telemetry/"+type+"/"+deviceId+"/values/timeseries?interval="+INTERVAL+"&limit="+LIMIT+"&agg="+AGG+"&keys="+key+"&startTs="+str(startTs)+"&endTs="+str(endTs),headers=headers)
        #print("Request to SOURCE ThingsBoard - response code: ", r.status_code)
    except Exception as e:
        print("\nAn exception occurred while trying to obtain and print the timeseries from SOURCE Thigsboard: ", e)
        logging.error('Timeseries request to device '+deviceId+' with key '+key+' failed.')

    # Define the timeseries to upload
    TIMESERIES = r.json()
    #print("Fetched timseries: ", TIMESERIES)
    
    logging.info('Timeseries request to device '+deviceId+' with key '+key+' was successful.')
	
    # Return the result of the GET request
    return TIMESERIES

'''
@Name postData(ip,port,user,password,deviceId,key,startTs,endTs)
@Return Returns a timeseries with the response to the HTTP RESTful request
@Parameters
    ip: ip address of target ThingsBoard
    port: port used by the target ThingsBoard
    token: authorization token
    deviceId: id of the device to read
    key: key of the timeseries to read
    timeseries: actual array containing the timeseries to upload: the last element shall be the one with the OLDEST unix timestamp
@Notes The function reads all the database entries associated with the device and key, with a LIMIT of 200000 and no aggregation
'''
def postData(ip,port,X_AUTH_TOKEN,deviceId,type="DEVICE",data="[]"):
    # Define the headers of the request
    headers = {'Content-Type': 'application/json','Accept':'application/json','X-Authorization': 'Bearer '+X_AUTH_TOKEN}

    # Perform the POST request to send timeseries
    try:
        r = requests.post("https://"+str(ip)+":"+str(port)+"/api/plugins/telemetry/"+type+"/"+deviceId+"/timeseries/ANY",headers=headers,data=data)
    except Exception as e:
        print("\nAn exception occurred while trying to send the timeseries to TARGET Thigsboard: ", e)
        logging.error('Timeseries POST request to device '+deviceId+' failed.')


'''
@Name sendData(ip,port,deviceToken,key,timeseries)
@Return None
@Parameters
    ip: ip address of target ThingsBoard
    port: port used by the target ThingsBoard
    deviceToken: token of the device to upload
    key: key of the timeseries to upload
    timeseries: actual array containing the timeseries to upload: the last element shall be the one with the OLDEST unix timestamp
@Notes This function uploads a timeseries (passed as argument) via MQTT
'''
def sendData(ip,port,deviceToken,key,timeseries):
    
    # Create MQTT client
    client = mqtt.Client()

    # Set access token
    client.username_pw_set(deviceToken)

    # Connect to ThingsBoard using default MQTT port and 60 seconds keepalive interval
    client.connect(ip, int(port), 60)
    client.loop_start()

    # Declare data format
    data = {"ts":0, "values":{key:0}}

    # Upload the timeseries with the proper timestamps and values
    try:
        
        # Send all the TIMESERIES values via MQTT, START FROM THE LAST ELEMENT SINCE IT IS THE OLDEST ONE
        for i in tqdm(range(len(timeseries[key])-1, -1, -1), desc='Uploading data to TARGET ThingsBoard'):

            value = timeseries[key][i]['value']
            ts = timeseries[key][i]['ts']

            data['ts'] = ts
            data['values'][key] = value

            # Send data to ThingsBoard via MQTT
            client.publish('v1/devices/me/telemetry', json.dumps(data), 1)
            #print("Upload timestamp: ", datetime.fromtimestamp(ts/1000), " | Raw data: ", data)

            # THE DELAY IS NECESSARY TO AVOID THE ThingsBoard "WEB_SOCKET: TOO MANY REQUESTS" ERROR
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("The user manually interrputed the MQTT upload using keyboard.")
        logging.error('Timeseries upload to device '+deviceToken+' with key '+key+' failed.')
        pass
    else:
        print("Data successfully published via MQTT.")

    logging.info('Timeseries upload to device '+deviceToken+' with key '+key+' was successful.')
	
    # Close the MQTT connections
    client.loop_stop()
    client.disconnect()

'''
@Name saveToFile(key,timeseries,file)
@Return None
@Parameters
    key: key of the timeseries to save on file
    timeseries: actual array containing the timeseries to save
    file: name of the file to use for saving
@Notes This function saves into a file a timeseries
'''
def saveToFile(key,timeseries,file):
    
    try:
        
        # Open the file in append mode
        file = open(file, 'a+')

        # Temporary variable to save timeseries entries
        data = {"ts":0, "value":0}
        
        # Iterate the timeseries and append to file, FROM THE LAST ELEMENT SINCE IT IS THE OLDEST ONE
        for i in tqdm(range(len(timeseries[key])-1, -1, -1), desc='Saving data to local file'):

            value = timeseries[key][i]['value']
            ts = timeseries[key][i]['ts']

            data['ts'] = ts
            data['value'] = value

            file.write(json.dumps(data) + "\n")
        
        # Close the file when finished
        file.close()

    except Exception as exception:
    
        print("An error occoured while saving the data into local text file: ", exception)
        logging.error('An error occoured while saving the data into local text file: ' + file)

'''
@Name readFromFile(key,file)
@Return timeseries
@Parameters
    key: key of the timeseries to read from file
    file: name of the file to use for reading
@Notes This function reads a timeseries from a file
'''
def readFromFile(key,file):
    
    timeseries = []
	
    try:
        
        # Open the file in append mode
        file = open(file, 'r')

        for line in file:
            timeseries.append(json.loads(line))
        
        # Close the file when finished
        file.close()
		
		# Format and return the correct timeseries
        response = {key: timeseries}
        return response

    except Exception as exception:
    
        print("An error occoured while reading the data from local text file: ", exception)
        logging.error('An error occoured while reading the data from local text file.')
		
		