import csv
import random
import sys, os
import time
import socket
import json, configparser
# from openhab import OpenHAB
import re
import pathlib
# import openhab.oauth2_helper
import requests
#import RaspberryPieIpAddressMonitor as rp
import urllib3 

# print("Starting Sensing.py")
# fp = open('Sensing.txt', 'x')
# fp.close()
# print("Test output", flush=True)


# The path variable is passed when the script is called 
Curpath = os.getenv('CURPATH', '/usr/src/app') # SD card storage
RAM_PATH = os.getenv('RAMPATH', '/dev/shm') # RAM storage

print(f'Current path for Sensing.py: {Curpath}', flush=True)
text_file_path = RAM_PATH #temporary text files going to be stored in the RAM 




urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)





########################
# FUNCTION DEFINITIONS #
########################

# $$$$$$$$$ UTILITY FUNCTIONS ##############################################

############################################################
# update time interval reached flag
# param: previous time stamp, time interval for next time stamp
# return: a boolean flag indicating if next time stamp should be taken
# status: complete
def update_time_flag(previous_time, interval):
    a=abs(int(time.time() - previous_time))
    if abs(int(time.time() - previous_time)) >= interval:
        return True
    else:
        return False


############################################################
# purpose: print msg to a text file
# parameters: file to print to, message
# return: true if success, false otherwise
# status: complete
def msg_to_file(file_name, message):
    with open(file_name, "a") as file:
        file.write(message)
        file.write("$")
        return True
    return False

############################################################
# purpose: print msg to a csv file
# parameters: file to print to, message
# return: true if success, false otherwise
# status: complete
def data_to_csv_file(file_name, data):
    with open(os.path.join(Curpath,file_name), 'a', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        # write multiple rows
        writer.writerows(data)
        return True
    return False


############################################################
# purpose: convert string / int to boolean
# parameters: string / int
# return: true if success, false otherwise
# status: complete
def ConvertToBoolean(val):
    if (val == '1' or val == 'True' or val == 1):
        return True
    return False


############################################################
# purpose: flip switches, for testing
# return: current value of the switching device
# status: complete
def flip(j):
    if j == 0:
        return 1
    else:
        return 0


# $$$$$$$$$ INITIALIZAtiON FUNCTIONS ##############################################

############################################################
# purpose: Read and convert the json formated program debug file and customer configuration file to dictionary format
# param: location of configuration file (eg: "configCustomer.ini")
# return: dictionary containing configuration info
# Configuration Dictionary Structure
#       Webserver Address: str
#       PHP Path: str
#       PC IP Address: str
#       Database Send Per Second: str
#       Nodes: dict
#       Sensing Devices: dict
#       Control Devices: dict
# status: complete
def json_to_dict(filename, flag):
    fp = open(filename, 'r')
    data = json.load(fp)
    fp.close()
    if (flag is not None):
        if (ConvertToBoolean(flag['config_to_dict_debug_flag'])):
            print("Customer Config data in Dictionary Format\n")
            print(data)
        else:
            print("Program Debug flags in Dictionary Format\n")
            print(data)
    return data

# $$$$$$$$$$$ Application functions ######################################

############################################################
# purpose: compose message 0 - combine elements of company info into a single string,
# parameters: IP address of PC, company name, company phone number, company street address
# return: string representing all company info
# status: complete 6/29/2021, might need datalength
def pack_company_info_msg_0(company_name,my_ip_address, pc_name):
    msg = "0|{}|{}|{}".format(company_name,my_ip_address, pc_name)
    if ConvertToBoolean(flag['pack_company_info_msg_debug_flag']):
        print(msg)
    return msg

############################################################
# purpose: compose message 1 -Combine sensor data
# parameters: name of the PC, node name, port id, sensor type, unit, lower limit, upper limit,equipment
# return: dictionary with flag
# status: completed on 11-18-21
def pack_sensor_info_msg_1(pc_name, node_name, sensor_name, port_type,sensor_type, brandname,unitname,
                           unit_symbol, lower_limit, upper_limit,equipment,label,model, raspberry_pi):
    msg = "1|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}".format(pc_name, node_name, sensor_name, port_type,brandname,
                                                            sensor_type, unitname,unit_symbol, lower_limit,
                                                            upper_limit, equipment,label,model,raspberry_pi)
    if ConvertToBoolean(flag['pack_sensor_info_msg_debug_flag']):
        print(msg)
    return msg


############################################################
# purpose: compose message 2 - combine elements of sensing data message into a single string
# parameters: device name, IP address of PC, sensor data
# return: string representing all company info
# status: complete, might need datalength
def pack_sensor_data_msg_2_v1(node_name, port_id, sensor_data):
    msg = "2|{}|{}|{}|{}".format(time.time(), node_name, port_id, sensor_data)
    if ConvertToBoolean(flag['pack_sensor_data_msg_debug_flag']):
        print(msg)
    return msg


def pack_sensor_data_msg_2_v2(pc_name,node_name, port_name, sensor_data):
    time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    msg = "2|{}|{}|{}|{}|{}".format(time_str, pc_name,node_name, port_name, sensor_data)
    if ConvertToBoolean(flag['pack_sensor_data_msg_debug_flag']):
        print(msg)
    return msg

def pack_sensor_data_msg_2_v3(pc_name,node_name, port_name, sensor_data):
    time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    msg = "{}|{}|{}|{}|{}*".format(time_str, pc_name,node_name, port_name, sensor_data)
    if ConvertToBoolean(flag['pack_sensor_data_msg_debug_flag']):
        print(msg)
    return msg

############################################################
# purpose: compose message 3 - combine elements of control message into a single string
# parameters: name of control device, port name of control device, control device type, control device lower limit, control device upper limit
# return: message containing control device information
# status: complete 6/30/2021, might need datalength
def pack_sensor_info_msg_3(pc_name, node_name, control_port_name,porttype, brandname,controltype, unitname, unitsymbol, control_lower_limit,
                           control_upper_limit, equipment_controlled,label,model, raspberry_pi):
    msg = "3|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}".format(pc_name, node_name, control_port_name,porttype, brandname,controltype, unitname, unitsymbol, control_lower_limit,
                                                            control_upper_limit, equipment_controlled,label,model,raspberry_pi)

    if ConvertToBoolean(flag['pack_control_msg_debug_flag']):
        print(msg)
    return msg




############################################################
# purpose: converts output of sensors (eg. Voltage) into actual meaning (eg. CO2 level)
# parameters: sensor output, upper and lower bound of sensor output, upper and lower bound of meaning
# return: meaning of sensor output
# status: completed and tested 6/29/2021

########## afr  processing data add cali--LK
def output_to_meaning(output, output_lb, output_ub, meaning_lb, meaning_ub):
    output_real = output - output_lb
    output_range_real = output_ub - output_lb
    meaning_range_real = meaning_ub - meaning_lb
    ratio = output_real / output_range_real
    meaning = (ratio * meaning_range_real) + meaning_lb
    # if debug_output_to_meaning_flag is True:
    #     print("...")
    return meaning


############################################################
# purpose: process sensor data as it is collected, 3 types so far
# parameters: previous average min or max, new sensor data, number of data values collected so far, type of processing (1=avg, 2=min, 3=max)
# return: postprocessing value
# status: complete
def process_data(previous_value, new_value, num_values_collected, process_type, sensor):
    new_value= new_value* sensor["Calibration"]
    if num_values_collected == 0:
        return new_value
    if process_type == 1:  ## AVERAGE ##
        postprocessingValue = ((previous_value * (num_values_collected - 1)) + new_value) / (num_values_collected)
    elif process_type == 2:  ## MINIMUM ##
        if previous_value > new_value:
            postprocessingValue = new_value
        else:
            postprocessingValue = previous_value
    elif process_type == 3:  ## MAXIMUM ##
        if previous_value > new_value:
            postprocessingValue = previous_value
        else:
            postprocessingValue = new_value
    else:
        print("invalid process type")
    # debug flag
    # exception
    return postprocessingValue


############################################################
# purpose: decode message 4 - extract info from database command (msg from database)
# parameters: command sent from database
# return: all elements of the command stored in separate variables
# command message format:
# status: complete
def decode_database_command(database_command):
    start_index = 0
    counter = 0
    for i in range(0, len(database_command), 1):
        if database_command[i] == "|":
            counter += 1
            if counter == 1:
                msgID = database_command[start_index, i]
            elif counter == 2:
                device_name = database_command[start_index, i]
            elif counter == 3:
                ip_address = database_command[start_index, i]
            elif counter == 4:
                value = database_command[start_index, i]
            start_index = i + 1
    timestamp = database_command[start_index, len(database_command)]
    return msgID, device_name, ip_address, value, timestamp


############################################################
# purpose: prepare and send message 0
# parameters: sensor data, ip address
# return: none
# status: complete
def Prepare_and_Send_Message0(systemData, IPAddress):
    companyInfo = pack_company_info_msg_0( systemData["CompanyName"],IPAddress,  systemData["PCName"])
    msg_to_file(os.path.join(text_file_path, "FormattedSystemData.txt"), companyInfo)
    ff = open(os.path.join(text_file_path, "CommunicationFlag.txt"), "w+")
    ff.close()


############################################################
# purpose: prepare and send message 1
# parameters: sensor data
# return: none
# status: complete
def Prepare_and_Send_Message1(systemData):
    for sensor in systemData["SensingPorts"]:
        sensorMsg = pack_sensor_info_msg_1(systemData["PCName"],
                                           sensor["NodeName"],
                                           sensor["PortName"],
                                           sensor["PortType"],
                                           sensor["SensorType"],
                                           sensor["BrandName"],
                                           sensor["InputValueUnitName"],
                                           sensor["InputValueUnitSymbol"],
                                           sensor["InputMeaningLowerBound"],
                                           sensor["InputMeaningUpperBound"],
                                           sensor["AttachedToEquipment"],
                                           sensor["SensorPortLabel"],
                                           sensor["SensorModel"],
                                           sensor["AssociatedRaspberryPiUnit"]
                                           )
        msg_to_file(os.path.join(text_file_path, "FormattedSystemData.txt"), sensorMsg)
        ff = open(os.path.join(text_file_path, "CommunicationFlag.txt"), "w+")
        ff.close()


############################################################
# purpose: prepare and send message 3
# parameters: sensor data
# return: none
# status: complete
def Prepare_and_Send_Message3(systemData):
    for switch in systemData["SwitchingPorts"]:
        switchMsg = pack_sensor_info_msg_3(systemData["PCName"],
                                           switch["NodeName"],
                                           switch["PortName"],
                                           switch["PortType"],
                                           switch["BrandName"],
                                           switch["ControlType"],
                                           switch["InputValueUnitName"],
                                           switch["InputValueUnitSymbol"],
                                           switch["LowerLimit"],
                                           switch["UpperLimit"],
                                           switch["AttachedToEquipment"],
                                           switch["PortLabel"],
                                           switch["Model"],
                                           switch["AssociatedRaspberryPiUnit"])

        msg_to_file(os.path.join(text_file_path, "FormattedSystemData.txt"), switchMsg)
        ff = open(os.path.join(text_file_path, "CommunicationFlag.txt"), "w+")
        ff.close()




############################################################
def Prepare_and_Send_Message2(systemData, previous_database_send_time):
    if update_time_flag(previous_database_send_time, int(systemData["DatabaseSendIntervalInSeconds"])):
        packed_msg_processed=""
        for sensor in systemData["SensingPorts"]:
            if(sensor["IsDataReadyToSent"]==1):
                packed_msg = pack_sensor_data_msg_2_v3(systemData["PCName"],
                                                       sensor["NodeName"],
                                                       sensor["PortName"],
                                                       sensor["ProcessedValue"])

                packed_msg_processed=packed_msg_processed+packed_msg
                sensor["ProcessedValue"] = 0
                sensor["IsDataReadyToSent"] = 0
        if( packed_msg_processed!=""):
            packed_msg_processed='2|' + packed_msg_processed
            msg_to_file(os.path.join(text_file_path, "FormattedSystemData.txt"), packed_msg_processed)
            ff = open(os.path.join(text_file_path, "CommunicationFlag.txt"), "w+")
            ff.close()
        if ConvertToBoolean(flag['msg_to_file_debug_flag']):
            print(packed_msg_processed)
            print('*****************************************************************************************')
        previous_database_send_time = time.time()
    return systemData, previous_database_send_time

#############################$$$$$$$$$$ Network Integraty Check ########################################





###############################################################################


###########################################################
# purpose: checks if a node is alive
# parameters: nodeid
# return: True, if  node is alive else False
# status: complete,

def CheckNodeStatus(nodename, associated_raspi, RetryCount=0):
    nodeStatuslabel='sensor.'+nodename.replace('-','')+'_node_status'
    url=systemData["UrlFetchSensorDataAndStatus"] \
        .replace("<ip_address_homeAssist>",associated_raspi["ip_address_homeAssist"]) \
        .replace("<portHomeAssist>",associated_raspi["portHomeAssist"]) \
        .replace("<entity_id>",nodeStatuslabel) #tag
    print(url, flush=True)
    print(nodeStatuslabel, flush=True)
    print("Inside checkNodeStatus", flush=True)
    try:
        response=requests.get(url, headers=associated_raspi["headers"])
        print(response.status_code, flush=True)
        if(response.status_code==200):
            status=response.json()['state']
            print(f"Status of {nodename}: {status}", flush=True)
            if(status in ('alive','asleep')):
                return True
        elif RetryCount<1 and not (response.ok):
            #rp.UpdateIPAddressForRaspberryPie(associated_raspi)
            return CheckNodeStatus(nodename, associated_raspi,RetryCount+1)
        return False
    except:
       return False

############################################################
# purpose: read all sensor data based on each of their sampling inervals
# parameters: sensor data
# return: sensor data
# status: complete
def Read_All_Sensor_Data(systemData):
    SensorDataStatus=[]
    for sensor in systemData["SensingPorts"]:
        if update_time_flag(sensor["PreviousSampleTime"],
                            sensor['PollingIntervalInSeconds']):
            label =sensor["PortType"]+'.'+sensor["NodeName"].replace('-','') + "_" + sensor["PortName"]
            print(label, flush=True)
            value=0
            associated_raspi = next((unit for unit in systemData["RaspberryPiUnits"] if unit["UnitName"] == sensor["AssociatedRaspberryPiUnit"]), None)
            if associated_raspi is  None:
                print("Error: No associated raspi found for sensor: " + sensor["NodeName"] + " " + sensor["PortName"], flush=True)
                continue;
            if CheckNodeStatus(sensor["NodeName"],associated_raspi): #tag
                print('----------------------------------------', flush=True)
                value=read_sensor_data(label, associated_raspi)
                sensor_reading = output_to_meaning(value,float(sensor["InputValueLowerBound"]),float(sensor["InputValueUpperBound"]),float(sensor["InputMeaningLowerBound"]),float(sensor["InputMeaningUpperBound"]))
            else:
                sensor_reading=99999

            sensor["ProcessedValue"] = sensor_reading
            # sensorData["Sensing Devices"][sensor]["Processed Value"] = process_data(sensorData["Sensing Devices"][sensor]["Processed Value"], sensor_reading, sensorData["Sensing Devices"][sensor]['Num Values Collected'], sensorData["Sensing Devices"][sensor]['Filter Method'])
            proccessedData = process_data(sensor["ProcessedValue"], sensor_reading,
                                          sensor['NumValuesCollected'],
                                          sensor['FilterMethod'], sensor)
            sensor["PreviousSampleTime"] = time.time()
            sensor["IsDataReadyToSent"]=1
            tstamp=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            dataArray = [tstamp,sensor["NodeName"],sensor["PortName"],value, sensor_reading]
            #if ConvertToBoolean(flag['read_sensor_data_debug_flag']):
            if(True): # fixthis
                print("Node: " + str(sensor["NodeName"]), flush=True)
                print("Port Type: " + str(sensor["PortType"]), flush=True)
                print("Label: " + label, flush=True)
                print("Sensor Reading: " + str(sensor_reading), flush=True)
                #print("proccessedData: " + str(proccessedData), flush=True)
                print('----------------------------------------', flush=True)
            if ConvertToBoolean(flag["check_sensor_data_validity_flag"]):
                SensorDataStatus.append(dataArray)
    if ConvertToBoolean(flag["check_sensor_data_validity_flag"]):
        data_to_csv_file('/SensorDataFile.csv',SensorDataStatus)
    return systemData


############################################################
# purpose: collect data from sensors
# parameters: name of the node that the device is connected to, ID of the sensing device, z-wave network
# return: current value of the sensor device
# status: complete
def read_sensor_data(sensor_id,associated_raspi,RetryCount=0):
    try:
        url=systemData["UrlFetchSensorDataAndStatus"] \
            .replace("<ip_address_homeAssist>",associated_raspi["ip_address_homeAssist"]) \
            .replace("<portHomeAssist>",associated_raspi["portHomeAssist"]) \
            .replace("<entity_id>",sensor_id)
        response=requests.get(url, headers=associated_raspi["headers"]) #tag
        print(f"URL used: {url}", flush=True)
        print(f"Read sensor response: {response}", flush=True)

        if response.status_code==200:
           currentValue=response.json()['state']
           if str(currentValue).lower() =="off":
              return 0
           if str(currentValue).lower() =="on":
              return 1
           currentValue = re.sub("[^0-9^.]", "", str(currentValue))
           currentValue = (0.00 if currentValue == "" else float(currentValue))
           return currentValue
        elif RetryCount<1 and not (response.ok):
            #rp.UpdateIPAddressForRaspberryPie(associated_raspi)
            return read_sensor_data(sensor_id,associated_raspi,RetryCount+1)
        return 0.00

    except Exception as e:
        print('WARNING!!!!!!!!!!!!!!!!!' + sensor_id + ' NOT FOUND/ NOT AVAILABLE\n\n\n -----------------\n\n', flush=True)
        currentValue=0.00
        print(e, flush=True)
        print('\n ***************************************************************************************************** \n ', flush=True)
    return currentValue






# $$$$$$$$$$ Adjusting Node Config ########################################


############################################################
# purpose: to set the sesitivity of sensor reading
# parameters: network
# return: none
# status: complete,
def SetSensorReadingSensitivity(network):
    for node in network.nodes:
        network.nodes[node].set_config_param(67, 1)
        network.nodes[node].set_config_param(68, 60)
















# $$$$$$$ the main starts here ###############################################
global url
global headers

if __name__ == "__main__":
    configDebug = os.path.join(Curpath, "ConfigurationFiles", "configDebug.json")
    flag = json_to_dict(configDebug, None)

    configCustomer = os.path.join(Curpath, "ConfigurationFiles", "configCustomer.json")
    systemData = json_to_dict(configCustomer, flag)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    IPAddress = s.getsockname()[0]
    s.close()
    Prepare_and_Send_Message0(systemData, IPAddress)
    Prepare_and_Send_Message1(systemData)
    Prepare_and_Send_Message3(systemData)
    #rp.UpdateNetworkDetailsForRasperryPieInBulk(systemData["RaspberryPiUnits"])
    previous_database_send_time = 0

    while True:
        systemData = Read_All_Sensor_Data(systemData)
        systemData, previous_database_send_time = Prepare_and_Send_Message2(systemData, previous_database_send_time)
        #rp.RefreshIPAddressForRaspberryPiUnitsBulk(systemData["RaspberryPiUnits"])
