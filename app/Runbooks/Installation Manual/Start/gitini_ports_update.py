import os
import json
import configparser
import socket

# Define file names
INPUT_JSON_FILE = "input.json"
GIT_INI_FILE = "git.ini"

# Function to find a free port
def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("0.0.0.0", 0))  
        return s.getsockname()[1]

# Function to get system IP
def get_system_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception as e:
        print(f"Error retrieving system IP: {e}")
        return "127.0.0.1"

# Custom config parser to preserve case
class CustomConfigParser(configparser.ConfigParser):
    def optionxform(self, optionstr):
        return optionstr

# Load JSON data
with open(INPUT_JSON_FILE, "r", encoding="utf-8") as json_file:
    data = json.load(json_file)

# Extract values from JSON
company_name = data["company_name"]
company_display_name = data["company_display_name"]
communication_email = data["communication_email"]
sms = data["sms"]
needed_instances = data["needed_instances"]
instances = data["instance_details"]

# Process instance details
instance_names = ",".join([inst["name"] for inst in instances])
seed_data = ",".join([inst["seedata"] for inst in instances])

# Determine available ports
system_ip = get_system_ip()
ports = [str(find_free_port()) for _ in range(needed_instances + 3)]  # Extra ports for servers
app_server_port, web_client_port, smtp_port = ports[-3:]  # Assign last 3 ports

# Read and update git.ini
config = CustomConfigParser()
config.read(GIT_INI_FILE, encoding="utf-8")

# Update values
config["gitdetails"]["home_dir"] = company_name
config["communication"]["email_id"] = communication_email
config["communication"]["sms_id"] = sms
config["other"]["instances"] = str(needed_instances - 1)
config["other"]["INSTANCE_NAMES"] = instance_names
config["other"]["SEED_DATA"] = seed_data
config["other"]["ports"] = ",".join(ports[:-3])  # Assign first `needed_instances` ports
config["other"]["APP_SERVER_HOST"] = system_ip
config["other"]["APP_SERVER_PORT"] = app_server_port
config["other"]["APP_SERVER_DOCKER_PORT"] = app_server_port
config["other"]["WEB_CLIENT_APPLICATION_NAME"] = company_display_name
config["other"]["WEB_CLIENT_PORT"] = web_client_port
config["other"]["WEB_CLIENT_DOCKER_PORT"] = web_client_port
config["other"]["SMTP_HOST"] = system_ip
config["other"]["SMTP_PORT"] = smtp_port

# Write updated config back to file
with open(GIT_INI_FILE, "w", encoding="utf-8") as configfile:
    config.write(configfile, space_around_delimiters=False)

print("Updated git.ini successfully!")
