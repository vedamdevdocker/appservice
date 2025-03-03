#!/bin/bash

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

# Run the Python script
echo "Running 01_start.py..."
python3 01_start.py

echo "Waiting for 2 seconds..."
sleep 2
echo "Resuming script execution."

echo "Running update_configini_file.py..."
python3 update_configini_file.py

# Extract home_dir from git.ini
home_dir=$(awk -F'=' '/^home_dir/{print $2}' git.ini | tr -d ' ')

# Ensure the home_dir is created
if [ -d "$home_dir" ]; then
    echo "Home directory '$home_dir' found. Applying permissions..."
    sudo chmod -R 777 "$home_dir/config" "$home_dir/start"
    sudo chmod 777 "$home_dir/config.ini"
    sudo chmod 777 "$home_dir/docarize.sh"
    echo "Permissions applied successfully."

    # Run run_python3.sh from the 'instance' directory
    if [ -d "$home_dir/config/instance" ]; then
        echo "Found 'instance' directory. Running run_python3.sh..."
        cd "$home_dir/config/instance" || exit
        sudo ./run_python3.sh
    else
        echo "Error: 'instance' directory not found in '$home_dir/config'."
    fi

    # Run run_python2.sh from the 'config' directory
    echo "Running run_python2.sh..."
    cd .. || exit  # Moves up to the config directory
    sudo ./run_python2.sh
else
    echo "Error: Home directory '$home_dir' was not found."
fi

# Run docarize.sh if present
echo "Switching to home directory and running docarize.sh..."
cd .. || exit  # Moves to Home directory
if [ -f "docarize.sh" ]; then
    sudo ./docarize.sh
else
    echo "Error: docarize.sh not found."
fi

echo "Installation complete!"
