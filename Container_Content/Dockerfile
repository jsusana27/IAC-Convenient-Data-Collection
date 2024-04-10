# Based around the python3 image
FROM python:3.10.10

# Set the containers working directory 
WORKDIR /usr/src/app

# Set the path environment variable 
ENV CURPATH=/usr/src/app
ENV RAMPATH=/dev/shm
ENV seeStdout=True

# Install requirements not in the standard library 
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Put local files into the working directory of the image
COPY . .

# Declare the BackupData directory as a volume
# VOLUME /usr/src/app/BackupData

# Start running the root process 
CMD ["python3", "RootProcess.py"]

