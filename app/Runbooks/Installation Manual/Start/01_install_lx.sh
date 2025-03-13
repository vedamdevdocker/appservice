#!/bin/bash

set -e  # Exit script on any error

# Update the system and install dependencies
echo "Updating package list and installing dependencies..."
sudo yum update -y

# Check and install curl
if ! command -v curl &>/dev/null; then
    echo "Installing curl..."
    sudo yum install -y curl
else
    echo "curl is already installed. Skipping..."
fi

# Check and install GCC, GCC-C++, and make
if ! command -v gcc &>/dev/null || ! command -v g++ &>/dev/null || ! command -v make &>/dev/null; then
    echo "Installing GCC, GCC-C++, and make..."
    sudo yum install -y gcc gcc-c++ make
else
    echo "GCC, GCC-C++, and make are already installed. Skipping..."
fi

# Check and install Docker Compose
if ! command -v docker-compose &>/dev/null; then
    echo "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    echo "Docker Compose is already installed. Skipping..."
fi

# Check and install Git
if ! command -v git &>/dev/null; then
    echo "Installing Git..."
    sudo yum install -y git
else
    echo "Git is already installed. Skipping..."
fi

# Check and install Python
if ! command -v python3 &>/dev/null; then
    echo "Installing Python and pip..."
    sudo yum install -y python3
else
    echo "Python is already installed. Skipping..."
fi

# Check and install Docker
if ! command -v docker &>/dev/null; then
    echo "Installing Docker..."
    sudo amazon-linux-extras enable docker
    sudo yum install -y docker
    sudo service docker start
    sudo systemctl enable docker
    sudo usermod -aG docker ec2-user
else
    echo "Docker is already installed. Skipping..."
fi

# Verify installations
echo "Verifying installations..."
git --version
python3 --version
pip3 --version
docker --version

echo "Running a test Docker container..."
sudo docker run hello-world

# Create swap file if it doesn't exist
if ! swapon --show | grep -q '/swapfile'; then
    echo "Creating swap file..."
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo "/swapfile none swap sw 0 0" | sudo tee -a /etc/fstab
else
    echo "Swap file already exists. Skipping..."
fi

# Set current directory
CURR_DIR=$(pwd)

# Read git.ini file
GIT_INI="$CURR_DIR/git.ini"
if [ ! -f "$GIT_INI" ]; then
    echo "Error: git.ini file not found."
    exit 1
fi

# Update git.ini file with client input and free ports
if [ -f "$CURR_DIR/gitini_ports_update.py" ]; then
    echo "Running gitini_ports_update.py..."
    python3 "$CURR_DIR/gitini_ports_update.py"
    if [ $? -ne 0 ]; then
        echo "Error: gitini_ports_update.py execution failed."
        exit 1
    fi
fi

# Run update_configini_file.py
if [ -f "$CURR_DIR/update_configini_file.py" ]; then
    echo "Running update_configini_file.py..."
    python3 "$CURR_DIR/update_configini_file.py"
    if [ $? -ne 0 ]; then
        echo "Error: update_configini_file.py execution failed."
        exit 1
    fi
fi

read -p "Press Enter to continue..."

# Run 01_start.py
echo "Running 01_start.py..."
python3 "$CURR_DIR/01_start.py"
if [ $? -ne 0 ]; then
    echo "Error: 01_start.py execution failed."
    exit 1
fi

# Extract home_dir from git.ini
HOME_DIR=$(awk -F'=' '/^home_dir/{print $2}' "$GIT_INI" | tr -d ' ')
if [ -z "$HOME_DIR" ]; then
    echo "Error: home_dir not found in git.ini."
    exit 1
fi

# Ensure home_dir exists
if [ ! -d "$CURR_DIR/$HOME_DIR" ]; then
    echo "Error: Home directory $HOME_DIR not found."
    exit 1
fi

# Copy config.ini from CURR_DIR to HOME_DIR
if [ -f "$CURR_DIR/config.ini" ]; then
    cp -f "$CURR_DIR/config.ini" "$CURR_DIR/$HOME_DIR/"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to copy config.ini to $HOME_DIR."
        exit 1
    fi
else
    echo "Warning: config.ini not found in $CURR_DIR."
fi

# Apply permissions to home_dir/config and other required files
echo "Applying permissions..."
sudo chmod -R 777 "$CURR_DIR/$HOME_DIR/config" "$CURR_DIR/$HOME_DIR/start"
sudo chmod 777 "$CURR_DIR/$HOME_DIR/config.ini"
sudo chmod 777 "$CURR_DIR/$HOME_DIR/docarize.sh"
echo "Permissions applied successfully."

# Run run_python3.sh from 'instance' directory inside 'config'
if [ -d "$CURR_DIR/$HOME_DIR/config/instance" ]; then
    echo "Found 'instance' directory. Running run_python3.sh..."
    cd "$CURR_DIR/$HOME_DIR/config/instance" || exit
    sudo ./run_python3.sh
else
    echo "Error: 'instance' directory not found in '$HOME_DIR/config'."
fi

# Run run_python2.sh from 'config' directory
echo "Running run_python2.sh..."
cd "$CURR_DIR/$HOME_DIR/config" || exit
sudo ./run_python2.sh

# Switch to home directory and run docarize.sh if present
echo "Switching to home directory and running docarize.sh..."
cd "$CURR_DIR/$HOME_DIR" || exit
if [ -f "docarize.sh" ]; then
    sudo ./docarize.sh
else
    echo "Warning: docarize.sh not found."
fi

echo "Script execution completed!"
