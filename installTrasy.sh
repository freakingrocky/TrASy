#!/bin/bash

# Function to open a new terminal window and run a command
open_terminal() {
    local cmd="$1"

    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal -- bash -c "$cmd; exec bash"
    elif command -v xterm &> /dev/null; then
        xterm -hold -e "$cmd"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        osascript -e "tell application \"Terminal\" to do script \"$cmd\""
    else
        echo "No compatible terminal emulator found. Please install gnome-terminal, xterm, or use a macOS system."
        exit 1
    fi
}

# Commands to run in separate terminal windows
open_terminal "cd /d Controllers && mvn install:install-file -Dfile=mssql-jdbc-12.6.3.jre11.jar -DgroupId=com.microsoft.sqlserver -DartifactId=mssql-jdbc -Dversion=12.6.3.jre11 -Dpackaging=jar"