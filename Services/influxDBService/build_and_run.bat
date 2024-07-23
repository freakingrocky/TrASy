@echo off
REM Stop the container if it is running
docker stop influxDBService

REM Remove the container if it exists
docker rm influxDBService

REM Build the Docker image
docker build -t cpp-webserver .

REM Run the Docker container with the specified name
docker run -d -p 1010:1010 --name influxDBService cpp-webserver

echo Docker container influxDBService is up and running on port 1010
