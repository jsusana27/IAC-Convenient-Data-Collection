import os
import multiprocessing  # allows for multiple CPU cores to be used to run different programs in parallel 
import subprocess  # allows for other programs/scripts to be called from this program
import contextlib
import select
import urllib3

# CURPATH is an environment variable created by the Dockerfile 
Curpath = os.getenv('CURPATH', '/usr/src/app')
RAM_PATH = os.getenv('RAMPATH', '/dev/shm') # ENV RAMPATH=/dev/shm
log_file_path = os.path.join(Curpath, "BackupData", "overnightlog.txt") # store the data logs in a text file 

# The following path will only use RAM for storage 
RAM_storage_path = '/tmp/convenient-data-collection'
os.makedirs(RAM_storage_path, exist_ok=True)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Execute Script, outputs the standard error if applicable 
def execute_script(script_path):
    try:
        subprocess.run(['python', script_path], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing {script_path}: {e}\nError Output:\n{e.stderr}")



def labeled_exec_script(script_path):
    script_name = os.path.basename(script_path)  # Extract the script name from the path
    try:
        # Start the subprocess and specify stdout and stderr to be piped
        with subprocess.Popen(['python', script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            # Monitor the stdout
            for line in process.stdout:  # This will also capture stderr if you want them combined
                print(f"{line.strip()} <-- from {script_name}")  # Append script name to each output line
               # with open(log_file_path, mode="a") as file:
                #    file.write(f"{line.strip()} <-- from {script_name} \n")

            # Check for any errors, appending the script name as well
            _, stderr = process.communicate()
            if stderr:
                print(f"Error executing {script_name}:\n{stderr.strip()} <-- from {script_name}")
                #with open(log_file_path, mode="a") as file:
                 #   file.write(f"Error executing {script_name}:\n{stderr.strip()} <-- from {script_name}")
    except Exception as e:
        print(f"Error executing {script_name}: {e} <-- from {script_name}")


def database_output(script_path):
    script_name = os.path.basename(script_path)  # Extract the script name from the path
    try:
        # Start the subprocess and specify stdout and stderr to be piped
        with subprocess.Popen(['python', script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            # Monitor the stdout
            for line in process.stdout:  # This will also capture stderr if you want them combined
                if script_name == 'DatabaseWrite.py':
                    print(f"{line.strip()} <-- from {script_name}\n\n\n")  
            # Check for any errors, appending the script name as well
            _, stderr = process.communicate()
            if stderr:
                print(f"Error executing {script_name}:\n{stderr.strip()} <-- from {script_name}")
    except Exception as e:
        print(f"Error executing {script_name}: {e} <-- from {script_name}")


# Main Function 
if __name__ == '__main__':
    try:
        os.remove(os.path.join(Curpath, ".oauth2_token"))
        os.remove(os.path.join(RAM_storage_path, ".oauth2_token"))
    except Exception:
        pass
    try:
        os.remove(os.path.join(Curpath, "CommunicationFlag.txt"))
        os.remove(os.path.join(RAM_storage_path, "CommunicationFlag.txt"))
    except Exception:
        pass

    processes = [
        os.path.join(Curpath, 'Sensing.py'),
        os.path.join(Curpath, 'ActuatorControl.py'),
        os.path.join(Curpath, 'DatabaseWrite.py')
    ]

    numProcesses = len(processes)

    print("Starting root process: ")
 # this sets up the parallel processing
    with contextlib.suppress(KeyboardInterrupt):
        #print("Inside with")
        pool = multiprocessing.Pool(processes=numProcesses)
        #pool.map(execute_script, processes)
        #pool.map(debug_exec_script, processes)
        pool.map(execute_script, processes) 
        pool.close()
        pool.join()
