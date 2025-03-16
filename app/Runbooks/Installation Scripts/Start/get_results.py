import os
import configparser
import docker
import socket
import requests

# Custom configparser that preserves case and formatting
class CaseInsensitiveConfigParser(configparser.ConfigParser):
    def optionxform(self, optionstr):
        return optionstr  # Preserve case

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

CONFIG_FILE = os.path.join(HOME_DIR, "config.ini")
DB_INSTANCES_DIR = os.path.join(HOME_DIR, "db_instances")
RESULTS_FILE = os.path.join(HOME_DIR, "results.txt")

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
        client = docker.from_env()
        containers = client.containers.list(all=True)
        container_details = "Container Details:\n"
        
        for container in containers:
            container_info = container.attrs
            image_name = container_info["Config"]["Image"]
            volumes = container_info["Mounts"]
            volume_list = [v["Name"] for v in volumes if "Name" in v]
            
            container_details += (
                f"Name: {container.name}\n"
                f"Status: {container.status}\n"
                f"Image: {image_name}\n"
                f"Volumes: {', '.join(volume_list) if volume_list else 'No volumes mounted'}\n"
                f"Access Container: docker exec -it {container.name} /bin/sh\n"
            )

            if volume_list:
                for volume in volume_list:
                    container_details += f"Inspect Volume: docker volume inspect {volume}\n"

            container_details += "\n"
        
        return container_details
    except Exception as e:
        print(f"Error getting container details: {e}")
        return "Error retrieving container details.\n"

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

generate_environment_details()
