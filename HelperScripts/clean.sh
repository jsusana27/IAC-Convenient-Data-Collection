#!/bin/bash

# Check the value of the cleaned state from the file
if [ "$(cat cleaned)" = "True" ]; then
    echo "You have already cleaned."
elif [ "$(cat cleaned)" = "False" ]; then
    echo y | docker system prune 
    docker rmi test:test
    # After cleaning, update the cleaned file to True
    echo "True" > cleaned
else
    echo "Nothing has been run. No need to clean."
fi





# # Check the value of the environment variable 'cleaned'
# if [ "$cleaned" = "True" ]; then
#   echo "You have already cleaned"
# elif [ "$cleaned" = "False" ]; then
#     echo y | docker system prune 
#     docker rmi test:test
#     cleaned="True"
#     export cleaned # make cleaned available to run.sh
# else
#   echo "Nothing has been run. No need to clean. "
# fi
