import sys
import argparse
import yaml
import logging
from datetime import datetime, timedelta
import time

from lib.auth import auth
from lib.customers import getCustomerAssets
from lib.devices import getCustomerDevices
from lib.timeseriesKeys import timeseriesKeys
from lib.checkTarget import checkTarget
from lib.keyFilter import keyFilter
from lib.timeseries import getData, postData
from lib.postDataFormat import postDataFormat


'''
@Notes This is the argument parser of the script
'''
# This sections parses the input arguments and saves them into constant variables
parser = argparse.ArgumentParser(description="This script performs a data migration between two different instances of ThingsBoard servers.")

parser.add_argument("-s", action="store", dest="sourceCustomerId", type=str, default="",
                    help="Specify the source customer ID", required=True)
parser.add_argument("-t", action="store", dest="targetCustomerId", type=str, default="",
                    help="Specify the target customer ID", required=True)
parser.add_argument("-i", action="store", dest="initialTs", type=str, default="",
                    help="Specify initial UNIX timestamp", required=True)
parser.add_argument("-e", action="store", dest="endTs", type=str, default="",
                    help="Specify final (ending) UNIX timestamp", required=True)
parser.add_argument("-f", action="store", dest="filter", type=str, default="None",
                    help="Specify the key filter", required=False)
parser.add_argument("-x", action="store_true", dest="checkTargetData", default=False,
                    help="Check if target data already exists", required=False)
parser.add_argument("-v", action="store_true", dest="verbose", default=False,
                    help="Show data", required=False)
parser.add_argument("-w", action="store_true", dest="postData", default=False,
                    help="Actually POST data to the target!", required=False)

args = parser.parse_args()

CONFIG_FILE = "./migrationConf.yml"
SOURCE_CUSTOMER_ID = args.sourceCustomerId
TARGET_CUSTOMER_ID = args.targetCustomerId
KEY_FILTER = args.filter
STARTTS = int(args.initialTs)
ENDTS = int(args.endTs)
CHECK_TARGET_DATA = args.checkTargetData
POST_DATA = args.postData
VERBOSE = args.verbose



AN_HOUR = 60 * 60
startDate = datetime.fromtimestamp(STARTTS)
endDate = datetime.fromtimestamp(ENDTS)
diff = ENDTS - STARTTS

print("start:", startDate)
print("end  :", endDate)

if POST_DATA:
    print("*** You are about to send data to the server, please think twice! ***")
    time.sleep(2)
    print("*** Ok, let's go! ***")
    time.sleep(0.5)
else:
    time.sleep(0.5)

'''
@Notes This is the config file reader of the script
'''
try:
    with open(CONFIG_FILE, 'r') as ymlfile: cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
    # Save here all the configuration variables
    SOURCE_TB_ADDRESS = cfg['source']['host']
    SOURCE_TB_PORT = cfg['source']['port']
    SOURCE_TB_USER = cfg['source']['user']
    SOURCE_TB_PASSWORD = cfg['source']['password']
    TARGET_TB_ADDRESS = cfg['target_http']['host']
    TARGET_TB_PORT = cfg['target_http']['port']
    TARGET_TB_USER = cfg['target_http']['user']
    TARGET_TB_PASSWORD = cfg['target_http']['password']
    LOG_FILE = cfg['log']['file']
    DB_FILE = cfg['db']['file']
    ymlfile.close()
    
except Exception as exception:
    print("An error occoured while reading the configuration file:", exception)
    print("Is it configured correctly?")
    sys.exit()

# Open and configure logger
logging.basicConfig(filename=LOG_FILE, filemode='a+', format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%d-%b-%y %H:%M:%S')
# Set minimum log level to "info"
logging.getLogger().setLevel(logging.INFO)
# Log something
logging.info('The script has been correctly initialized.')

# get the auth tokens
SOURCE_AUTH_TOKEN = auth(SOURCE_TB_ADDRESS,SOURCE_TB_PORT,SOURCE_TB_USER,SOURCE_TB_PASSWORD)
TARGET_AUTH_TOKEN = auth(TARGET_TB_ADDRESS,TARGET_TB_PORT,TARGET_TB_USER,TARGET_TB_PASSWORD)

sourceAssets = getCustomerAssets(SOURCE_TB_ADDRESS,SOURCE_TB_PORT,SOURCE_AUTH_TOKEN,SOURCE_CUSTOMER_ID)
targetAssets = getCustomerAssets(TARGET_TB_ADDRESS,TARGET_TB_PORT,TARGET_AUTH_TOKEN,TARGET_CUSTOMER_ID)
checkTarget(sourceAssets, targetAssets)

sourceDevices = getCustomerDevices(SOURCE_TB_ADDRESS,SOURCE_TB_PORT,SOURCE_AUTH_TOKEN,SOURCE_CUSTOMER_ID)
targetDevices = getCustomerDevices(TARGET_TB_ADDRESS,TARGET_TB_PORT,TARGET_AUTH_TOKEN,TARGET_CUSTOMER_ID)
checkTarget(sourceDevices, targetDevices)

for asset in sourceAssets:
    assetId = asset['id']['id']
    assetName = asset['name']
    targetAsset = next((x for x in targetAssets if x['name'] == assetName), None)
    targetAssetId = targetAsset['id']['id']
    targetAssetName = targetAsset['name']
    print("\n =>", assetId, assetName, '=>', targetAssetId, targetAssetName)
    keys = timeseriesKeys(SOURCE_TB_ADDRESS,SOURCE_TB_PORT,SOURCE_AUTH_TOKEN,assetId,'ASSET')
    for key in keys:
        if keyFilter("ASSET", KEY_FILTER, key):
            current = startDate
            while current < endDate:
                startTs = int(current.timestamp()) * 1000
                endTs = int(current.timestamp() + AN_HOUR) * 1000
                sourceData = getData(SOURCE_TB_ADDRESS,SOURCE_TB_PORT,SOURCE_AUTH_TOKEN,assetId,key,startTs,endTs,'ASSET')
                targetData = {}
                if CHECK_TARGET_DATA:
                    targetData = getData(TARGET_TB_ADDRESS,TARGET_TB_PORT,TARGET_AUTH_TOKEN,targetAssetId,key,startTs,endTs,'ASSET')

                if isinstance(targetData, dict) and key in targetData:
                    print('Error: data already exists in target', current, assetName, key, len(targetData[key]))
                else:
                    print(current, assetName, key, len(sourceData[key]))
                    if VERBOSE:
                        print(sourceData[key])
                    if POST_DATA:
                        formattedData = postDataFormat(sourceData, key)
                        if formattedData is not None:
                            postData(TARGET_TB_ADDRESS,TARGET_TB_PORT,TARGET_AUTH_TOKEN,targetAssetId,'ASSET',formattedData)

                time.sleep(0.25)
                if current == endDate:
                    break
                current = current + timedelta(seconds=(AN_HOUR + 1))
                if current >= endDate:
                    current = endDate
        else:
            continue
    #     break
    # break

for device in sourceDevices:
    deviceId = device['id']['id']
    deviceName = device['name']
    targetDevice = next((x for x in targetDevices if x['name'] == deviceName), None)
    targetDeviceId = targetDevice['id']['id']
    targetDeviceName = targetDevice['name']
    print("\n =>", deviceId, deviceName, '=>', targetDeviceId, targetDeviceName)
    keys = timeseriesKeys(SOURCE_TB_ADDRESS,SOURCE_TB_PORT,SOURCE_AUTH_TOKEN,deviceId,'DEVICE')
    for key in keys:
        if keyFilter("DEVICE", KEY_FILTER, key):
            current = startDate
            while current < endDate:
                startTs = int(current.timestamp()) * 1000
                endTs = int(current.timestamp() + AN_HOUR) * 1000
                sourceData = getData(SOURCE_TB_ADDRESS,SOURCE_TB_PORT,SOURCE_AUTH_TOKEN,deviceId,key,startTs,endTs,'DEVICE')
                targetData = {}
                if CHECK_TARGET_DATA:
                    targetData = getData(TARGET_TB_ADDRESS,TARGET_TB_PORT,TARGET_AUTH_TOKEN,targetDeviceId,key,startTs,endTs,'DEVICE')

                if isinstance(targetData, dict) and key in targetData:
                    print('Error: data already exists in target', current, deviceName, key, len(targetData[key]))
                else:
                    print(current, deviceName, key, len(sourceData[key]))
                    if VERBOSE:
                        print(sourceData[key])
                    if POST_DATA:
                        formattedData = postDataFormat(sourceData, key)
                        print("postData Devices")
                        if formattedData is not None:
                            postData(TARGET_TB_ADDRESS,TARGET_TB_PORT,TARGET_AUTH_TOKEN,targetDeviceId,'DEVICE',formattedData)

                time.sleep(0.25)
                if current == endDate:
                    break
                current = current + timedelta(seconds=(AN_HOUR + 1))
                if current >= endDate:
                    current = endDate
        else:
            continue
    #     break
    # break


logging.info('Execution finished.')
print('\nExecution finished.')


