import json
import os
import pathlib
import time
# from openhab import OpenHAB
# import openhab.oauth2_helper
import requests
import urllib3

# get the path where data is stored 
Curpath = os.getenv('CURPATH', '/usr/src/app')
print(f'Current path for RaspberryPieAddressMonitor.py: {Curpath}')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def json_to_dict(filename):
    fp = open(filename, 'r')
    data = json.load(fp)
    fp.close()
    return data

def FetchIPAddressForRaspberryPie(unitName):
    print('Fetching IP address for Raspberry Pie')
    url=webserver_address.format("7", unitName)
    try:
        response = requests.get(url, verify=False)
        if response.ok:
            responseCleaned=response.text.replace("Database connected", '')
            if responseCleaned != "" and response.text is not None:
                networkInfo= [json.loads(idx.replace("'", '"')) for idx in [responseCleaned]]
                return networkInfo[0][0]
        return None
    except Exception as c:
        print('Exception in the call request to update URL')
        return None

def UpdateIPAddressForRaspberryPie(unit):
    info=FetchIPAddressForRaspberryPie(unit['UnitName'])
    if info is not None:
        unit["ip_address_homeAssist"]=info['Ip_Address']
        unit["portHomeAssist"]=info['PortID']
        unit["PreviousIpSynchronizationTimeStamp"]=time.time()
    return

def UpdateNetworkDetailsForRasperryPieInBulk(RaspberryPiUnits):
    print('Initializing network details for Raspberry Pie')
    for unit in RaspberryPiUnits:
        UpdateIPAddressForRaspberryPie(unit)
    return

def CheckIfIPAddressForRaspberryPieRequireRefresh(unit):
    if unit["PreviousIpSynchronizationTimeStamp"] == 0:
        return True
    else:
        interval=time.time()-unit["PreviousIpSynchronizationTimeStamp"]
        return (interval>config["RaspberrySynchronizingIntervalInSeconds"])


def RefreshIPAddressForRaspberryPiUnitsBulk(units):
    for unit in units:
        if CheckIfIPAddressForRaspberryPieRequireRefresh(unit):
            print('Refreshing IP address for Raspberry Pie')
            UpdateIPAddressForRaspberryPie(unit)
    return



js = os.path.join(Curpath, "ConfigurationFiles", "configCustomer.json")
config = json_to_dict(js)
webserver_address = config['WebserverAddress']
