import json
import sys, os
import pathlib
import time
# from openhab import OpenHAB
# import openhab.oauth2_helper
import requests
import urllib3
#import RaspberryPieIpAddressMonitor as rp

print("Starting ActuatorControl.py", flush=True)

Curpath = os.getenv('CURPATH', '/usr/src/app')
RAM_PATH = os.getenv('RAMPATH', '/dev/shm')
print(f'Current path for ActuatorControl.py: {Curpath}', flush=True)

text_files_folder_path = RAM_PATH # os.path.join(Curpath, "TextFiles")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
lastActuatorSyncTime=time.time()

def read_request_from_database(address, msg_id):
    try:
        response = requests.get(address.format(msg_id, "x"), verify=False)
        if response.ok:
            responseCleaned=response.text.replace("Database connected", '')
            if responseCleaned != "" and response.text is not None:
                actuatorRequest = [json.loads(idx.replace("'", '"')) for idx in [responseCleaned]]
                if actuatorRequest[0] !=[]:
                    print(actuatorRequest[0], flush=True)
                return actuatorRequest[0]
            else:
                return []
        else :
            return []
    except Exception as c:
        raise c


def json_to_dict(filename):
    fp = open(filename, 'r')
    data = json.load(fp)
    fp.close()
    return data

def msg_to_file(file_name, message):
    with open(file_name, "a") as file:
        file.write(message)
        file.write("$")
        return True
    return False



def SendUpdatedCommad(command,associated_raspi ):
    print('Sending updated command to DB', flush=True)
    message=pack_sensor_data_msg_5(config['PCName'],command["NodeName"], command["PortName"],command["CommandValue"], command["ID"],'DONE' if CheckCommandExecution(command,associated_raspi) else 'FAILED')
    return message

def WriteToFile(message):
    msg_to_file(os.path.join(text_files_folder_path, "FormattedSystemDataActuator"), message)
    ff = open(os.path.join(text_files_folder_path, "CommunicationFlagActuator.txt"), "w+")
    ff.close()

def pack_sensor_data_msg_5(pc_name,node_name, port_id, actuator_status,id, commandStatus):
    time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    msg = "{}|{}|{}|{}|{}|{}|{}*".format(time_str,pc_name ,node_name, port_id, actuator_status,id, commandStatus)
    return msg

def AcknowledgeCommand(command):
    msg=""
    for command in actuator_requests:
        actuator = next((unit for unit in config["SwitchingPorts"] if unit["NodeName"] ==  command["NodeName"]), None)
        associated_raspi = next((unit for unit in config["RaspberryPiUnits"] if unit["UnitName"] == actuator["AssociatedRaspberryPiUnit"]), None)
        if associated_raspi is  None:
            print("Error: No associated raspi found for sensor: " + command["NodeName"] + " " + command["PortName"], flush=True)
            continue

    msg=msg+SendUpdatedCommad(command,associated_raspi )
    if msg!="":
        message="5|"+msg
        WriteToFile(message)

def update_time_flag(previous_time, interval):
    if abs(int(time.time() - previous_time)) >= interval:
        return True
    else:
        return False

def CheckCommandExecution(command,associated_raspi, RetryCount=0):
    label=GenerateLabelForActuator(command)
    url=config["UrlFetchSensorDataAndStatus"] \
        .replace("<ip_address_homeAssist>",associated_raspi["ip_address_homeAssist"]) \
        .replace("<portHomeAssist>",associated_raspi["portHomeAssist"]) \
        .replace("<entity_id>",label)
    response=requests.get(url, headers=associated_raspi["headers"])
    print(label, flush=True)
    print(response, flush=True)
    if response.status_code==200:
        state=response.json()['state']
        stateEncoded=1 if state=="on" else 0
        if command["CommandValue"] == stateEncoded.__str__():
            return True
    elif RetryCount<1 and not (response.ok):
        #rp.UpdateIPAddressForRaspberryPie(associated_raspi)
        return CheckCommandExecution(command,associated_raspi,RetryCount+1)
    return False

def ExecuteRequestCommand(entity_id,command,associated_raspi, RetryCount=0):
    url=config["UrlActuatorHandler"].replace("<ip_address_homeAssist>", associated_raspi["ip_address_homeAssist"]) \
        .replace("<portHomeAssist>", associated_raspi["portHomeAssist"])
    turn_on= True if command["CommandValue"]=='1' else False
    payload = {
        "entity_id": entity_id
    }

    if turn_on:
        urlExecute = url.replace("<ON_OR_OFF>", "on")
    else:
        urlExecute = url.replace("<ON_OR_OFF>", "off")

    response = requests.post(urlExecute, headers=associated_raspi["headers"], data=json.dumps(payload))

    if response.status_code == 200:
        print(f"Switch {entity_id} successfully turned {'on' if turn_on else 'off'}", flush=True)
        return
    elif RetryCount<1 and not (response.ok):
        #rp.UpdateIPAddressForRaspberryPie(associated_raspi)
        ExecuteRequestCommand(entity_id,command,associated_raspi,RetryCount+1)
        return
    else:
        print(f"Failed to toggle switch {entity_id}. Error: {response.text}", flush=True)
        return


def GenerateLabelForActuator(command):
    label=""
    if command["PortName"]=='':
        label=command["PortType"] +'.'+ command["NodeName"]
    else:
        label=command["PortType"] +'.'+ command["NodeName"]+'_'+ command["PortName"]
    return label


js = os.path.join(Curpath, "ConfigurationFiles", "configCustomer.json")
config = json_to_dict(js)
webserver_address = config['WebserverAddress']
#rp.RefreshIPAddressForRaspberryPiUnitsBulk(config["RaspberryPiUnits"])

print("Finished setup")

try:
    while True:
        actuator_requests = read_request_from_database(webserver_address, "4")
        #actuator_requests = []
        if actuator_requests!= []:
            #rp.RefreshIPAddressForRaspberryPiUnitsBulk(config["RaspberryPiUnits"])
            for command in actuator_requests:
                command['UpdatedCommand']=""
                label=GenerateLabelForActuator(command)
                actuator = next((unit for unit in config["SwitchingPorts"] if unit["NodeName"] ==  command["NodeName"]), None)
                associated_raspi = next((unit for unit in config["RaspberryPiUnits"] if unit["UnitName"] == actuator["AssociatedRaspberryPiUnit"]), None)
                print(associated_raspi)
                if associated_raspi is None:
                    print("Error: No associated raspi found for sensor: " + command["NodeName"] + " " + command["PortName"], flush=True)
                    continue
                ExecuteRequestCommand(label,command,associated_raspi)
            AcknowledgeCommand(actuator_requests)


except Exception as e:
    print('------------------------------------------------------------------------------------------------', flush=True)
    print('Error in ActuatorControl.py', flush=True)
    print(e, flush=True)
    print(e.__str__(), flush=True)
    print('-----------------------------------------------------------------------------------------------', flush=True)
    exit(1)
