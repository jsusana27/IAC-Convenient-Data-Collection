# IAC-Convenient-Data-Collection

## Raspberry Pi OS Version:
Raspberry Pi OS with desktop
Release date: March 15th 2024
System: 64-bit
Kernel version: 6.6
Debian version: 12 (bookworm)

## HAS Version & Other related:
HAS version 1.7.0

## Obtaining the Image 
- The latest image created should be stored on DockerHub. Any new images that are made and found to be stable can be pushed here.
- All of our image iterations can be found using this link: https://hub.docker.com/repository/docker/gtemplin/iac_convenient_data_collection/general
- The version with the highest number is the latest 

## Running the Container 
- For quick testing, you can build an image and run the container locally. There are some premade helper scripts for this purpose.
- The subdirectory 'Container_Content' will contain the Dockerfile (essentially building instructions), requirements.txt to list the Python program's dependencies, and the rest will be files to be placed within the image. 
- In the 'HelperScripts' subdirectory, you will find two shell scripts. One called 'run.sh' and another called 'clean.sh'.
- run.sh will go to 'Container_Content', build the image using the Dockerfile/dependencies, and then run the container.
- clean.sh can be ran once the running container is stopped, and it will delete the container and it's associated image. This is done so that only the most recent version of the image exists at any time. 
