@echo off
REM Stop the container if it is running
docker stop sqlDBService

REM Remove the container if it exists
docker rm sqlDBService

REM Build the Docker image
docker build -t cpp-webserver .

REM Run the Docker container with the specified name
docker run -d -p 1010:1010 --name sqlDBService cpp-webserver

echo Docker container sqlDBService is up and running on port 1010
