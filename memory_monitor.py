# Here's a Python script to get the CPU temperature and memory utilization of a Raspberry Pi.
import datetime
import os
import time
import sys 
import zipfile


# Memory that can be allocated without affecting system performance 
def get_memory_available():
    with open("/proc/meminfo", "r") as meminfo:
        meminfo_lines = meminfo.readlines()
    mem_total = 0
    mem_available = 0
    # Parse the necessary values
    for line in meminfo_lines:
        if "MemTotal" in line:
            mem_total = int(line.split()[1])
        elif "MemAvailable" in line:
            mem_available = int(line.split()[1])
    
    # Calculate the percentage of available memory
    if mem_total > 0:  # Prevent division by zero
        available_memory_percentage = (mem_available * 100.0) / mem_total
        return available_memory_percentage
    else:
        return "Memory total is zero, can't calculate percentage."

# This returns the percentage of total RAM completely free 
def get_memory_free():
    with open("/proc/meminfo", "r") as meminfo:
        meminfo_lines = meminfo.readlines()
    mem_total = 0
    mem_free = 0
    # Parse the necessary values
    for line in meminfo_lines:
        if "MemTotal" in line:
            mem_total = int(line.split()[1])
        elif "MemFree" in line:
            mem_free = int(line.split()[1])

    # Calculate the percentage of available memory
    if mem_total > 0:  # Prevent division by zero
        free_memory_percentage = (mem_free * 100.0) / mem_total
        return round(free_memory_percentage,2)
    else:
        return "Memory total is zero, can't calculate percentage."


# Returns the cpu utilization percentage for all cores 
def read_cpu_usage():
    """Reads CPU usage statistics from /proc/stat."""
    with open("/proc/stat", "r") as f:
        line = f.readline()
        # Extract the CPU time spent in various modes from the first line
        cpu_times = [float(value) for value in line.split()[1:]]
    return cpu_times
# Calcualte the CPU utilization in a 1 second period 
def calculate_cpu_usage(delay=1):
    start_times = read_cpu_usage()
    time.sleep(delay)
    end_times = read_cpu_usage()

    # Calculate time spent in each of the modes over the delay period
    delta_times = [end - start for start, end in zip(start_times, end_times)]
    total_delta_time = sum(delta_times)

     # Calculate the percentage of time spent idle / total time 
    idle_time = delta_times[3]  # The 4th value in the list corresponds to idle time
    idle_percentage = (idle_time / total_delta_time) * 100
    
    # Subtract idle percentage from 100 to get CPU utilization
    cpu_usage_percentage = 100 - idle_percentage
    return round(cpu_usage_percentage, 2)



def oldZip(mem_threshold, file_path, zipLocationPath, zipCount):
    mem_remaining = 100 - get_memory_free() # how much memory is remaining & completely unused 
    if mem_remaining <= mem_threshold:
        # Either create the zip file or append to the zip file 
        if zipCount == 0:
            with zipfile.ZipFile(zipLocationPath, 'w') as zip:
                zip.write(file_path, arcname=f'ZipArchive{zipCount}.txt')
        else:
            with zipfile.ZipFile(zipLocationPath, 'a') as zip:
                zip.write(file_path, arcname=f'ZipArchive{zipCount}.txt')
        zipCount += 1 
        os.remove(file_path) # Delete the non-zipped file to save space 
    return zipCount


# Determine if the backup text file is getting too large and needs to be zipped 
# also needs to know how many zips have occurred 
# directory is where the backup text file and zip files will be stored (/dev/shm as of now)
def zipIfNeeded(directory, zipCount, X_KB):
    # Get the size of the backup text file
    file2zip = os.path.join(directory,'BackupData.txt')
    file_size = os.path.getsize(file2zip)
    # Set where the zip file should be placed once created
    zipFullPath = os.path.join(directory, f'ZipArchive{zipCount}.zip')
    # If the file has reached X KB, compress it using zip 
    if file_size >= X_KB:
        # zip 'file2zip', have name when extracted be 'ZipArchive.txt', save zipped file to zipFullPath
        with zipfile.ZipFile(zipFullPath, 'w') as zip:
                zip.write(file2zip, arcname=f'ZipArchive{zipCount}.txt')
        # Indicate a zip has occurred, then delete the old .txt file to save space 
        zipCount += 1 
        os.remove(file2zip)
    return zipCount


# Extracts one of the zipped backups, places it in it's own text file, then returns path to the extracted text file
def unZip(directory, zipCount):
    # Path to the zip file to be extracted
    path2zip = os.path.join(directory, f'ZipArchive{zipCount}.zip')
    # Extract the zip file (should only be one)
    with zipfile.ZipFile(path2zip, 'r') as zip_ref:
        zip_ref.extract(f'ZipArchive{zipCount}.txt', directory)
    # Remove the .zip file since it has been extracted 
    os.remove(path2zip)
    # Return path to the extracted file
    extraction_path = os.path.join(directory, f'ZipArchive{zipCount}.txt')
    return extraction_path


def zipTest():
    file_path = '/home/admin/Senior-Design-Testing-Folder/convenient-data-collection/BackupTest.txt'
    zip_file_path = '/home/admin/Senior-Design-Testing-Folder/convenient-data-collection/BackupTest.zip'
    with zipfile.ZipFile(zip_file_path, 'w') as zip:
        zip.write(file_path, arcname='archive.txt')   
    # Getting the size of the original and zipped file
    original_size = os.path.getsize(file_path)
    zipped_size = os.path.getsize(zip_file_path)
    print(f'Original size: {original_size/1000000} MB\nZipped size: {zipped_size/1000000} MB')



if __name__ == "__main__":
    print("Doesn't run standalone")

else:
    print("Importing memory monitor related ")
  

