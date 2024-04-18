import json  # interact with json 
import sys, os  # interact with the operating system 
import requests  # used to make http requests or interact with   
import configparser # handle configuration files to store preferences 
import asyncio  # helps manage multiple IO related tasks 
import urllib3  # used for making requests to web servers through http 

import memory_monitor

print("Starting DatabaseWrite.py", flush=True)

Curpath = os.getenv('CURPATH', '/usr/src/app')
RAM_PATH = os.getenv('RAMPATH', '/dev/shm')
print(f'Current path for DatabaseWrite.py: {Curpath}', flush=True)

debug = False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

zipCount = 0 # will keep track of the number of zips that have occurred 

# format a message and send to database
# the asyncio loop lets this wait until complete w/o bottlenecking the whole program  
def send_to_database(address, msg):
    try:
        if msg!='':
            url=address.format(msg[0: 1], msg[2:])
            #print(url, flush=True)
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(sendData(url))
    except ConnectionError as c:
        return False
    except Exception as c:
        print(c, flush=True)
        return False

# uses an http get request to send the data 
async def sendData(url):
    print(url, flush=True)
    response= requests.get(url, verify=False)
    return bool(int(response.status_code)==200)


# uses python's file management function to append 
def write_to_backup(backup, data):
    with open(backup, "a") as _:
        _.write(data)
        return True
    return False


def delete_from_file(file_name, part_to_delete):
    file = open(file_name, "w+")
    file_contents = file.read()
    file_contents = remove_prefix(file_contents, part_to_delete)
    file.truncate()
    file.write(file_contents)
    file.close()


def remove_prefix(input_string, prefix):
    if prefix and input_string.startswith(prefix):
        return input_string[len(prefix):]
    return input_string

# Get webserver addtess
def json_to_dict(filename):
    fp = open(filename, 'r')
    data = json.load(fp)
    fp.close()
    return data


#####################################################
############# SETUP PORTION BELOW ###################
#####################################################   ggb

# the web server for a particular customer is extracted from a json file 
config_file_path = os.path.join(Curpath, "ConfigurationFiles", "configCustomer.json")
config = json_to_dict(config_file_path)
webserver_address = config['WebserverAddress']

# Create path to backup text file (placed in RAM)
backup_file_path = os.path.join(RAM_PATH, "BackupData.txt")
if not os.path.isfile(backup_file_path):
    with open(backup_file_path, "x") as f:
        print(f"Backup text file created in {backup_file_path}", flush=True) # File is created, 'f.close()' is called automatically

# if debug:
#     if not os.path.exists(backup_file_path):
#         with open(backup_file_path, 'w') as file:
#             file.write("Hello, Geeks!")
#         print("Wrote to file", flush=True)       
#     else:
#         print(f"The file '{backup_file_path}' already exists.", flush=True)



#####################################################
############# LOOPING PORTION BELOW #################
#####################################################

# If either of the flags are set, store the data from the file associated with it, then clear that file so that it can be used again later. 
# Once it sees that a flag is set for communication, it formats it and sends it to the database 
while True:
    communication_flag_path = os.path.join(RAM_PATH, "CommunicationFlag.txt") # fixthis should be going to RAM not disk. Maybe ask Chien if this is what it's supposed
    communication_flag_actuator_path = os.path.join(RAM_PATH, "CommunicationFlagActuator.txt")
    formatted_system_data_path = os.path.join(RAM_PATH, "FormattedSystemData.txt")
    formatted_system_data_actuator_path = os.path.join(RAM_PATH, "FormattedSystemDataActuator.txt")

    # Create fresh files to send, and reset flags 
    if os.path.isfile(communication_flag_path) or os.path.isfile(communication_flag_actuator_path):
        fileContents = ""
        if os.path.isfile(formatted_system_data_path):
            if os.path.isfile(communication_flag_path):
                try:
                    os.remove(communication_flag_path)
                except Exception:
                    print("CommunicationFlag is not deleted", flush=True)
                    pass               
                with open(formatted_system_data_path, "r+") as file:
                    fileContents = file.read()
                    file.seek(0)  # Move to the start of the file before truncating
                    file.truncate()

        elif os.path.isfile(formatted_system_data_actuator_path): 
            fileContentsActuator = ""
            if os.path.isfile(communication_flag_actuator_path):
                try:
                    os.remove(communication_flag_actuator_path)
                except Exception:
                    print("CommunicationFlagActuator is not deleted", flush=True)
                    pass
                with open(formatted_system_data_actuator_path, "r+") as file2:
                    fileContentsActuator = file2.read()
                    file2.seek(0)  # Move to the start of the file before truncating
                    file2.truncate()

        fileContents= fileContents + fileContentsActuator

        if debug:
            print("FILE CONTENTS: {}".format(fileContents), flush=True)


# Parse through the file contents until you get to the delimiter ($)
# After this you can send the stored message to the database 
        start_index = 0
        successfulSend=False
        for i in range(0, len(fileContents), 1):
            if fileContents[i] == "$":
                msg = fileContents[start_index: i] ## TRY DIFFERENT SUBSTRING METHOD
                if debug:
                    print("sending: {}".format(msg), flush=True)
                successfulSend = send_to_database(webserver_address, msg)
                start_index = i+1
                
        
# This portion backs up the data if it wasn't successful and sends any data in the backup text file to the database
        maxBackupSize = 500e6 # 500MB backup size 
        if not successfulSend:
            print("CONNECTION IS DOWN--BACKING UP DATA", flush=True)
            write_to_backup(backup_file_path, fileContents)
            # Check to see if memory utilization is too high, resulting in the backup text file requiring a zip 
            zipCount = memory_monitor.zipIfNeeded(RAM_PATH, zipCount, maxBackupSize)

        else:
            # Zip up the last instance to make sure the total memory is minimized (if another zip occurred previously)
            if zipCount > 0: 
                zipCount = memory_monitor.zipIfNeeded(RAM_PATH, zipCount, maxBackupSize) # Zip what's there now to prevent memory overuse 
                numBackups = zipCount
                # Loop through all the archives, unzip each individual file, send to database, and then delete the unzipped archive 
                for i in range(numBackups):
                    # Get one of the archived files, unzip and save to unzippedBackup path, write to the database
                    # Unzipped file is located in the ram path under Unzipped.txt
                    unzippedBackup = memory_monitor.unZip(RAM_PATH, i)
                    with open(unzippedBackup) as backup:
                        backupContents = backup.read()          
                    start_index = 0
                    for i in range(0, len(backupContents), 1):
                        if backupContents[i] == "$":
                            msg = backupContents[start_index: i]
                            successfulSend = send_to_database(webserver_address, msg)
                            start_index = i + 1
                            if successfulSend:
                                delete_from_file(backup_file_path, msg)
                    os.remove(unzippedBackup) # Delete the backup once parsed through it all 
                zipCount = 0 # reset to indicate required backups have been dealt with 

            # Managing backup when no zipping has occurred, and everything is in a single file 
            else:
                with open(backup_file_path) as backup:
                    backupContents = backup.read()
                start_index = 0
                for i in range(0, len(backupContents), 1):
                    if backupContents[i] == "$":
                        msg = backupContents[start_index: i]
                        successfulSend = send_to_database(webserver_address, msg)
                        start_index = i + 1
                        if successfulSend:
                            delete_from_file(backup_file_path, msg)
