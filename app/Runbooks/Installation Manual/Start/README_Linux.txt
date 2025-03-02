Installation and Setup Guide

	This guide provides step-by-step instructions to install the necessary dependencies, set up Docker, clone required repositories, 
	and containerize the web application.

Prerequisites

	Before running the installation, ensure that:
	You have access to an Amazon Linux 2 EC2 instance.
	You have a sudo user with permission to install packages.
	You have an active internet connection to download dependencies.

Step 1: Execute the Installation Script

	The installation process is automated using a shell script (01_install_lx.sh). This script performs the following tasks:

	1.1 Install Required Packages, Updates the system package list.
		Installs curl, gcc, git, python, and other dependencies.

	1.2 Install Docker and Docker Compose

		Enables Amazon Linux extras for Docker.
		Installs and starts the Docker service.
		Enables Docker to start on system boot.
		Adds the current user to the Docker group to allow running Docker commands without sudo.
		Installs Docker Compose.

	1.3 Configure Swap Memory

		Creates a 2GB swap file to enhance system performance.

	1.4 Run Python Setup Script

		Executes 01_start.py to begin the repository cloning and setup process.
		To execute the script, run the following commands:

		chmod +x 01_install_lx.sh
		./01_install_lx.sh

Step 2: Repository Cloning and Configuration

		After installation, 01_start.py will:
		Read configurations from the git.ini file.
		Clone the required repositories (AppService and WebClient).
		Set up the required directory structure.
		Copy installation manuals and relevant configuration files.
		Ensure that the git.ini file is properly configured before running the script.

Step 3: Permissions and Execution

		The script will check if the home directory exists as specified in git.ini and apply necessary permissions:
		Grants read/write/execute permissions to critical files and directories.
		Runs run_python3.sh and run_python2.sh scripts inside the appropriate directories.
		Executes the docarize.sh script to containerize the application.

Step 4: Verify Installation

		Once the setup is complete, verify that all installations were successful:
		docker --version
		git --version
		python --version
		pip3 --version
		Run a test Docker container to ensure proper installation:
		sudo docker run hello-world

Step 5: Running the Application
		To start the application inside a Docker container, navigate to the setup directory and run:
		sudo ./docarize.sh

		This will:
			Build the necessary Docker images.
			Start the application inside containers.
	
		To check running containers, use:
		docker ps
	
Troubleshooting

Common Issues & Fixes

	1.Permission Denied for Docker Commands
		Run sudo usermod -aG docker ec2-user
		Reboot the instance using sudo reboot

	2.Docker Daemon Not Running
		Start Docker manually using: sudo service docker start
	3.Repositories Not Cloning
		Ensure that Git credentials are correctly provided in git.ini.
		Run git clone manually to check for access issues.
Conclusion
	By following these steps, you have successfully:
		1. 	Installed Docker and necessary dependencies.
		2.	Cloned the required repositories.
		3.	Configured and set up the application inside Docker.
	Your web application is now ready to run in a containerized environment!