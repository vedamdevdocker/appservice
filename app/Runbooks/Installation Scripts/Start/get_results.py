import os
import configparser
import docker
import socket
import requests
import time
import sys
import json
import subprocess  # Import subprocess to run shell commands

# Custom configparser that preserves case and formatting
class CaseInsensitiveConfigParser(configparser.ConfigParser):
    def optionxform(self, optionstr):
        return optionstr  # Preserve case

# Function to check Docker permissions
def check_docker_permissions():
    try:
        # Check if the current user has access to Docker
        client = docker.from_env()
        # Try fetching the Docker version to see if we have access
        client.ping()
        print("Docker is accessible.")
    except docker.errors.DockerException as e:
        print(f"Error: Docker permissions issue - {e}")
        # Suggest adding the user to the 'docker' group
        print("You may need to add the user to the 'docker' group:")
        print("Run 'sudo usermod -aG docker $(whoami)' and then log out and log back in.")
        
        # Attempt to automatically add the user to the docker group (requires sudo)
        if os.geteuid() == 0:  # Check if the script is run with sudo (root user)
            try:
                user = os.getenv("USER")
                print(f"Attempting to add user '{user}' to docker group...")
                subprocess.run(["usermod", "-aG", "docker", user], check=True)
                print(f"User {user} has been added to the docker group. Please log out and log back in.")
                sys.exit(1)  # Exit after attempting to fix
            except subprocess.CalledProcessError as sub_e:
                print(f"Error while trying to add user to docker group: {sub_e}")
                sys.exit(1)  # Exit the script if the operation fails
        else:
            sys.exit(1)  # Exit if not running as root

# Define file paths based on custom HOME_DIR from git.ini
GIT_INI_PATH = os.path.join(os.getcwd(), "git.ini")
print(f"Checking for git.ini at: {GIT_INI_PATH}")

if not os.path.exists(GIT_INI_PATH):
    print(f"Error: git.ini not found at {GIT_INI_PATH}")
    exit(1)

git_config = CaseInsensitiveConfigParser()
git_config.read(GIT_INI_PATH)
print("git.ini loaded successfully.")

if "gitdetails" not in git_config or "home_dir" not in git_config["gitdetails"]:
    print("Error: 'home_dir' not found in [gitdetails] section of git.ini")
    exit(1)

HOME_DIR = os.path.join(os.getcwd(), git_config["gitdetails"]["home_dir"])
print(f"Resolved HOME_DIR: {HOME_DIR}")
HOME_DIR_NAME = os.path.basename(HOME_DIR)
print(f"Resolved HOME_DIR_NAME: {HOME_DIR_NAME}")

CONFIG_FILE = os.path.join(HOME_DIR, "config.ini")
DB_INSTANCES_DIR = os.path.join(HOME_DIR, "db_instances")
RESULTS_FILE = os.path.join(HOME_DIR, f"{HOME_DIR_NAME}_results.txt")

def get_config():
    try:
        config = configparser.ConfigParser()
        if not os.path.exists(CONFIG_FILE):
            raise FileNotFoundError(f"{CONFIG_FILE} not found.")
        config.read(CONFIG_FILE)
        return config
    except Exception as e:
        print(f"Error reading config: {e}")
        raise

def get_system_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception as e:
        print(f"Error getting system IP: {e}")
        return "127.0.0.1"

def get_public_ip():
    try:
        response = requests.get("https://api64.ipify.org?format=text", timeout=5)
        return response.text.strip()
    except Exception as e:
        print(f"Error getting public IP: {e}")
        return "Unknown"

def get_web_application_details(config, public_ip):
    system_ip = get_system_ip()
    web_client_port = config.get("WebClient", "WEB_CLIENT_PORT", fallback="")
    web_client_protocol = config.get("WebClient", "WEB_CLIENT_PROTOCOL", fallback="https")
    
    ui_url1 = f"{web_client_protocol}://{system_ip}:{web_client_port}"
    ui_url2 = f"{web_client_protocol}://localhost:{web_client_port}"
    ui_url3 = f"{web_client_protocol}://{public_ip}:{web_client_port}" if public_ip != "Unknown" else "Public IP not available"
    
    return f"Web Application Details:\nUI_URL1={ui_url1}\nUI_URL2={ui_url2}\nUI_URL3={ui_url3}\n"

def get_backend_application_details(config, public_ip):
    system_ip = get_system_ip()
    backend_port = config.get("AppService", "APP_SERVER_PORT", fallback="")
    backend_protocol = config.get("AppService", "APP_SERVER_PROTOCOL", fallback="https")
    
    api_url1 = f"{backend_protocol}://{system_ip}:{backend_port}"
    api_url2 = f"{backend_protocol}://localhost:{backend_port}"
    api_url3 = f"{backend_protocol}://{public_ip}:{backend_port}" if public_ip != "Unknown" else "Public IP not available"
    
    return f"Backend Application Details:\nAPI_URL1={api_url1}\nAPI_URL2={api_url2}\nAPI_URL3={api_url3}\n"

def get_database_details(config):
    db_host_ip = config.get("instances", "DB_SERVER_HOST_IP", fallback="localhost")
    instance_names = config.get("instances", "INSTANCE_NAMES", fallback="").split(',')
    ports = config.get("instances", "ports", fallback="").split(',')
    
    db_details = "Database Details:\n"
    for idx, instance in enumerate(instance_names):
        instance = instance.strip().lower()
        db_config_file = os.path.join(DB_INSTANCES_DIR, instance, "db_config.ini")
        
        if os.path.exists(db_config_file):
            db_config = configparser.ConfigParser()
            db_config.read(db_config_file)
            user = db_config.get("database", "user", fallback="unknown")
            password = db_config.get("database", "password", fallback="unknown")
            root_password = db_config.get("database", "ROOT_PASSWORD", fallback="unknown")
            db_details += (f"Instance: {instance.upper()}\n"
                           f"Host: {db_host_ip}\n"
                           f"Host: localhost\n"
                           f"Host: 127.0.0.1\n"
                           f"Port: {ports[idx]}\n"
                           f"User: {user}\n"
                           f"Password: {password}\n"
                           f"Root Password: {root_password}\n\n")
    return db_details

def get_container_details():
    try:
        home_dir_prefix = HOME_DIR_NAME.lower()
        result = subprocess.run(
            ["docker", "ps", "-a", "--format", "{{.ID}} {{.Names}}"], 
            capture_output=True, text=True, check=True
        )
        container_lines = result.stdout.strip().split("\n")

        if not container_lines or container_lines[0] == "":
            return "No matching containers found. Docker might not be running."

        container_details = "Filtered Container Details:\n"

        for line in container_lines:
            container_id, container_name = line.split(" ", 1)

            if not container_name.lower().startswith(home_dir_prefix):
                continue

            inspect_result = subprocess.run(["docker", "inspect", container_id], capture_output=True, text=True, check=True)
            container_info = json.loads(inspect_result.stdout)[0]

            status = container_info["State"]["Status"]
            image = container_info["Config"]["Image"]
            volumes = container_info.get("Mounts", [])

            volume_mappings = [
                f"{vol.get('Name', vol.get('Source', 'Unknown'))} -> {vol['Destination']}" 
                for vol in volumes
            ]
            
            print(f"DEBUG: Volumes for {container_name} -> {volumes}")  # Debugging line

            container_details += (
                f"Name: {container_name}\n"
                f"Status: {status}\n"
                f"Image: {image}\n"
                f"Volumes: {', '.join(volume_mappings) if volume_mappings else 'No volumes found'}\n"
                f"Access Container: docker exec -it {container_name} /bin/sh\n"
                "----------------------------------------\n"
            )

        return container_details if "Name:" in container_details else "No matching containers found."

    except subprocess.CalledProcessError as e:
        return f"Error retrieving container details: {e}"

def generate_environment_details():
    try:
        config = get_config()
        public_ip = get_public_ip()
        
        web_details = get_web_application_details(config, public_ip)
        backend_details = get_backend_application_details(config, public_ip)
        db_details = get_database_details(config)
        container_details = get_container_details()
        
        result_content = f"{web_details}\n{backend_details}\n{db_details}\n{container_details}"
        
        with open(RESULTS_FILE, "w") as file:
            file.write(result_content)
        
        print("Environment details written to results.txt")
    except Exception as e:
        print(f"Error generating environment details: {e}")

# Check Docker permissions before proceeding with the rest of the script
check_docker_permissions()

# Generate environment details
generate_environment_details()
