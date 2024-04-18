#!/bin/bash

# Read the full image name and tag from the file
image_full=$(cat image_full_details.txt)

# Check the value of the cleaned state from the file
if [ "$(cat cleaned)" = "True" ]; then
    echo "You have already cleaned."
elif [ "$(cat cleaned)" = "False" ]; then
    echo y | docker system prune 
    docker rmi "$image_full"  # remove the latest image you created 
    # After cleaning, update the cleaned file to True
    echo "True" > cleaned
else
    echo "Nothing has been run. No need to clean."
fi
