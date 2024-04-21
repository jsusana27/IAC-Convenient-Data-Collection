#!/bin/bash

# Home Assistant API endpoint for getting the configuration
#HA_ENDPOINT="http://homeassistant.local:8123/api/config"
#HA_ENDPOINT="http://134.68.225.201:8123/api/config"
HA_ENDPOINT="http://localhost:8123/api/config" # can use localhost, which will work regardless of internet connection 
SENSOR_ENDPOINT="http://localhost:8123/api/states/sensor." #http://localhost:8123/api/states/sensor.snode_102_node_status

# Your Long-Lived Access Token
ACCESS_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJmYjk5NGJlNzlhZGI0NjczOTc3NWMwMWMwZjk0YjYwNyIsImlhdCI6MTcxMzQ2NzU1NywiZXhwIjoyMDI4ODI3NTU3fQ.8k5Y4idmkfKkvVPPE7A-AfnEBRD00yRHI2mnzlnVff4"
# Function to test connectivity to the Home Assistant API
test_api_connectivity() {
    response=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer ${ACCESS_TOKEN}" \
              -H "Content-Type: application/json" \
              "${HA_ENDPOINT}")

    if [ "$response" -eq 200 ]; then
        echo "Success: Connected to the Home Assistant API."
    else
        echo "Error: Failed to connect to the Home Assistant API. HTTP Status Code: ${response}"
    fi
}


# read a sensor's data using the api
read_sensor_data(){
	USER_IN="$1"
	response=$(curl -s -H "Authorization: Bearer ${ACCESS_TOKEN}" \
                     -H "Content-Type: application/json" \
                     "${USER_IN}")
	if [ -n "$response" ]; then
        	echo "Success: Received data from the sensor."
        	echo "Sensor Value: ${response}"
    	else
        	echo "Error: Failed to get data from the sensor."
    	fi
}

# Main script execution
test_api_connectivity

echo "Input the sensor's entity id: "
read entity
SENSOR_CURL="$SENSOR_ENDPOINT$entity"
echo "URL: $SENSOR_CURL" 
read_sensor_data $SENSOR_CURL
