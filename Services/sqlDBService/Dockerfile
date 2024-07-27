# Use an official Ubuntu as the base image
FROM ubuntu:20.04

# Set environment variables to avoid prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    gnupg \
    odbcinst \
    unixodbc-dev \
    libboost-system-dev \
    libjsoncpp-dev \
    && rm -rf /var/lib/apt/lists/*

# Install the ODBC Driver 17 for SQL Server
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/msprod.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Build the application
RUN make

# Expose port 1010 to the outside world
EXPOSE 1011

# Run the application
CMD ["./sqlDBService"]
