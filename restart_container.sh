#!/bin/bash

# Stop and remove container
docker stop pasive_income_v1
docker rm pasive_income_v1

# Remove container
docker image rm pasive_income

echo "Build and Run container? (y/n)"
read response

if [ "$response" == "y" ]; then
    # Build container 
    docker build -t pasive_income .

    # Run container
    docker run -d -p 8000:8000 --name pasive_income_v1 

    # Get relevant data
    ip=$(docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $container_name)
    host_port=$(docker inspect --format='{{(index (index .NetworkSettings.Ports "8000/tcp") 0).HostPort}}' $container_name)
    host=$(curl ifconfig.me)

    echo "----------------------------------------------------"
    echo "Container Name: $container_name"
    echo "Container running in http://${host}:$port" 


else
    echo "Ok."
fi
