#!/bin/bash

# List Docker images whose names contain 'iac', case-insensitively
echo "Listing all Docker images related to IAC already created:"
docker images --format '{{.Repository}}:{{.Tag}}' | grep -i 'iac'
echo "-----------------------------------------------------------"

# Ask the user for the image name and tag
echo "Enter the Docker image name:"
read image_name
echo "Enter the Docker image tag:"
read image_tag

# Build directory for Dockerfile
build_dir="/home/admin/Conv-Data/IAC-Convenient-Data-Collection/Container_Content"

# Build and run the container. Use the host network for easier communication with homeassistant container
docker build -t "$image_name:$image_tag" "$build_dir"

#docker run --name test --network host -v /dev/shm:/dev/shm -v /home/admin/senior-design-testing-folder/local-volume:/usr/src/app/BackupData -it test:test /bin/bash

# Run the container
# Set up SD card volume and RAM stored volume
docker run --name "$image_name" \
  --network host \
  -v /dev/shm:/dev/shm \
  -v /home/admin/senior-design-testing-folder/local-volume:/usr/src/app/BackupData \
  -it "$image_name:$image_tag" /bin/bash
  #-dit "$image_name:$image_tag" /bin/bash 

echo "Running detached (in background)"

# Path to the 'cleaned' file
cleaned_file="cleaned"

# Check if the 'cleaned' file does not exist, is empty, or contains "True"
if [ ! -f "$cleaned_file" ] || [ ! -s "$cleaned_file" ] || [ "$(cat $cleaned_file)" = "True" ]; then
    # If the file doesn't exist, is empty, or contains "True", set it to "False"
    echo "False" > "$cleaned_file"
    echo "'cleaned' was not set to 'False', now set to 'False'"
else
    # If none of the above conditions are met, it implies the file exists, is not empty, and does not contain "True"
    echo "The 'cleaned' file was already set and does not contain 'True'."
fi


