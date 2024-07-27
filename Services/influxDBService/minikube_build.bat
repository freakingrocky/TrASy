& minikube -p minikube docker-env | Invoke-Expression
REM Stop the container if it is running
docker stop influxDBService

REM Remove the container if it exists
docker rm influxDBService

REM Build the Docker image
docker build -t influx-db-service:latest .

REM Run the Docker container with the specified name
docker run -d -p 1010:1010 --name influxDBService influx-db-service:latest

echo Docker container influxDBService is up and running on port 1010
