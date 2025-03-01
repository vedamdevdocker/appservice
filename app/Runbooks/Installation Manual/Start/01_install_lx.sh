c#!/bin/bash

# Update the system and install dependencies
echo "Updating package list and installing dependencies..."
sudo yum update -y
sudo yum install -y curl
sudo yum install -y gcc gcc-c++ make

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
echo "Installing Git..."
sudo yum install -y git

# Install Python 3.x and pip
echo "Installing Python  and pip..."
sudo yum install -y python

# Install Docker using amazon-linux-extras
echo "Installing Docker..."
sudo amazon-linux-extras enable docker
sudo yum install -y docker

# Start Docker service
echo "Starting Docker service..."
sudo service docker start

# Enable Docker service to start on boot
sudo systemctl enable docker

# Add ec2-user to the docker group (so you can run Docker without sudo)
sudo usermod -aG docker ec2-user

# Verify installations
echo "Verifying Git installation..."
git --version

echo "Verifying Python installation..."
python --version
pip3 --version

echo "Verifying Docker installation..."
docker --version

# Run a test Docker container
echo "Running a test Docker container..."
sudo docker run hello-world

# Run memory swap to cope up 1 GB memory 
echo "Creating swap file..."
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo "/swapfile none swap sw 0 0" | sudo tee -a /etc/fstab

# Run the Python script
echo "Running 01_start.py..."
python 01_start.py

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
        echo "Found 'instance' directory. Switching to it and running run_python3.sh..."
        cd "$home_dir/config/instance" || exit
        sudo ./run_python3.sh
    else
        echo "Error: 'instance' directory not found in '$home_dir/config'."
    fi

    # Run run_python2.sh from the 'config' directory
    echo "Switching to config directory and running run_python2.sh..."
	cd .. || exit  # Moves up to the config directory
    sudo ./run_python2.sh

else
    echo "Error: Home directory '$home_dir' was not found."
fi

echo "Switching to home directory and running docarize.sh..."
cd .. || exit  # Moves to Home directory 
sudo ./docarize.sh

echo "Installation complete!"