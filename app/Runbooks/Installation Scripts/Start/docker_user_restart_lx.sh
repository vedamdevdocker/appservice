#!/bin/bash

# Get the current username
USER_NAME=$(whoami)

# Check if the user is in the 'docker' group
if groups $USER_NAME | grep -q "\bdocker\b"; then
    echo "User '$USER_NAME' is already in the docker group. No need to restart."
    exit 0
else
    echo "User '$USER_NAME' is NOT in the docker group. Adding user and restarting..."
    
    # Add user to the docker group
    sudo usermod -aG docker $USER_NAME
    
    echo "User added to the docker group. Restarting the system..."
    sudo shutdown -r now
fi
