#!/bin/bash

# Stop the container if it is running
docker stop sqlDBService

# Remove the container if it exists
docker rm sqlDBService

# Build the Docker image
docker build -t cpp-webserver .

# Run the Docker container with the specified name
docker run -d -p 1010:1010 --name sqlDBService cpp-webserver

echo "Docker container sqlDBService is up and running on port 1010"
