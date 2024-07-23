# Use an official Ubuntu base image
FROM ubuntu:20.04

# Set the environment variable to non-interactive to avoid time zone prompt
ENV DEBIAN_FRONTEND=noninteractive

# Set the time zone
RUN ln -fs /usr/share/zoneinfo/UTC /etc/localtime && \
    apt-get update && \
    apt-get install -y tzdata

# Install required packages
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    cmake \
    make \
    g++ \
    wget \
    curl \
    libboost-system-dev \
    libboost-thread-dev \
    libssl-dev \
    libjsoncpp-dev

# Set the working directory
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Run make to build the application
RUN make

# Expose port 1010 to the outside world
EXPOSE 1010

# Define the command to run the app
CMD ["./testService"]
