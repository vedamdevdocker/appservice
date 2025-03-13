Windows Installation and Setup Guide

This guide provides step-by-step instructions to install the necessary dependencies, set up Docker, 
clone required repositories, and containerize the web application on a Windows machine.

Prerequisites
	Before running the installation, ensure that:
	Python is installed and added to the system path.
	Git is installed and accessible from the command line.
	Docker Desktop is installed and running.
	You have an active internet connection to download dependencies.

Step 1: Execute the Installation Script
	The installation process is automated using a batch script (01_install_win.bat). This script performs the following tasks:

		1.1 Check for Python Installation
			The script verifies if Python is installed.
			If Python is missing, an error message is displayed, and the script exits.

		1.2 Run Python Setup Script
			Executes 01_start.py to begin the repository cloning and setup process.
		
		To execute the script, run the following command in Command Prompt:
		01_install_win.bat

Step 2: Repository Cloning and Configuration

	1.	After installation, 01_start.py will:
	2.	Read configurations from the git.ini file.
	3.	Clone the required repositories (AppService and WebClient).
	4.	Set up the required directory structure.
	5.	Copy installation manuals and relevant configuration files.
	
	Ensure that the git.ini file is properly configured before running the script.

Step 3: Permissions and Execution
	The script will check if the home directory exists as specified in git.ini and apply necessary actions:
		Grants read/write/execute permissions to critical files and directories.
		Runs the docarize.bat script to containerize the application.

Step 4: Verify Installation
	Once the setup is complete, verify that all installations were successful:
		python --version
		git --version
		docker --version
	Run a test Docker container to ensure proper installation:
		docker run hello-world

Step 5: Running the Application

	To start the application inside a Docker container, navigate to the setup directory and run:
		docarize.bat
	This will:
		Build the necessary Docker images.
		Start the application inside containers.
	To check running containers, use:
		docker ps

Troubleshooting

	Common Issues & Fixes

	1.	Python Not Recognized
		Ensure Python is installed and added to the system PATH.
		Restart Command Prompt after installation.
		
	2.	Git Not Recognized
		Ensure Git is installed and accessible from the command line.
		Run git --version to verify.
		
	3.	Docker Desktop Not Running
		Open Docker Desktop and ensure it is running.
		Restart your computer if necessary.
		
	4.	Repositories Not Cloning
		Ensure that Git credentials are correctly provided in git.ini.
		Run git clone manually to check for access issues.

Conclusion

	By following these steps, you have successfully:
	Installed Python, Git, and Docker.
	Cloned the required repositories.
	Configured and set up the application inside Docker.
	Your web application is now ready to run in a containerized environment! 🚀