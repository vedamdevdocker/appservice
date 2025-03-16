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

# Check and install Python3 and pip3
if ! command -v python3 &>/dev/null; then
    echo "Installing Python3 and pip3..."
    sudo yum install -y python3 python3-pip
    sudo alternatives --install /usr/bin/python python /usr/bin/python3 1
else
    echo "Python3 is already installed. Skipping..."
fi

# Create symlink for python to point to python3
if ! command -v python &>/dev/null; then
    echo "Creating symlink for python..."
    sudo ln -s /usr/bin/python3 /usr/bin/python
else
    echo "Python symlink already exists. Skipping..."
fi

# Ensure pip is correctly linked (it should point to pip3 due to the python symlink)
if ! command -v pip &>/dev/null; then
    echo "Creating symlink for pip..."
    sudo ln -s /usr/bin/pip3 /usr/bin/pip
else
    echo "pip symlink already exists. Skipping..."
fi

# Check and install Docker
if ! command -v docker &>/dev/null; then
    echo "Installing Docker..."
  
    # Install Docker using dnf (Amazon Linux 2023)
    sudo dnf install -y docker
    
    # Start Docker service
    sudo systemctl start docker
    
    # Enable Docker to start on boot
    sudo systemctl enable docker
    
    # Add the ec2-user to the docker group
    sudo usermod -aG docker ec2-user
else
    echo "Docker is already installed. Skipping..."
fi

# Verify installations
echo "Verifying installations..."
git --version
python --version
pip --version
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

# Run Python scripts
for script in gitini_ports_update.py update_configini_file.py 01_start.py; do
    if [ -f "$CURR_DIR/$script" ]; then
        echo "Running $script..."
        python "$CURR_DIR/$script"
        if [ $? -ne 0 ]; then
            echo "Error: $script execution failed."
            exit 1
        fi
    fi
done

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
sudo chmod -R 777 "$CURR_DIR/$HOME_DIR/config" "$CURR_DIR/$HOME_DIR/Start"
sudo chmod 777 "$CURR_DIR/$HOME_DIR/config.ini"
sudo chmod 777 "$CURR_DIR/$HOME_DIR/docarize.sh"
echo "Permissions applied successfully."

# Run run_python.sh from 'instance' directory inside 'config'
if [ -d "$CURR_DIR/$HOME_DIR/config/instance" ]; then
    echo "Found 'instance' directory. Running run_python.sh..."
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

cd "$CURR_DIR" || exit

# Ensure 'docker' Python module is installed
echo "Checking for 'docker' Python module..."
if ! python -c "import docker" 2>/dev/null; then
    echo "'docker' module not found. Installing..."
    
    # Upgrade pip to the latest version
    pip install --upgrade pip
    
    # Install the latest version of urllib3
    pip install --upgrade urllib3
    
    # Now install the docker module
    pip install docker
    
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install 'docker' module."
        exit 1
    fi
else
    echo "'docker' module is already installed."
fi

# Run get_results.py to generate environment details
echo "Running get_results.py..."
if [ -f "get_results.py" ]; then
    python "get_results.py"
    if [ $? -ne 0 ]; then
        echo "Error: get_results.py execution failed."
        exit 1
    fi
else
    echo "Warning: get_results.py not found."
fi

echo "Script execution completed!"
