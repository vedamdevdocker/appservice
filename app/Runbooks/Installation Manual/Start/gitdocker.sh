#!/bin/bash

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
echo "Installing Python 3 and pip..."
sudo yum install -y python3

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
python3 --version
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

echo "Installation complete!"
