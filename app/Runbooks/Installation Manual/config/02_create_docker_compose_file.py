import os
import yaml
import configparser

def get_parent_directory():
    """Find the parent directory of the script."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_db_instances(parent_dir):
    """Get a list of subdirectories inside db_instances."""
    db_instances_path = os.path.join(parent_dir, "db_instances")
    if not os.path.exists(db_instances_path):
        raise FileNotFoundError(f"db_instances directory not found in {parent_dir}")
    return [d for d in os.listdir(db_instances_path) if os.path.isdir(os.path.join(db_instances_path, d))]

def read_config(config_path):
    """Read the config.ini file and return values."""
    config = configparser.ConfigParser()
    config.read(config_path)

    if "WebClient" not in config:
        raise ValueError("Missing [WebClient] section in config.ini")
        
    if "AppService" not in config:
        raise ValueError("Missing [AppService] section in config.ini")

    if "Global" not in config:
        raise ValueError("Missing [Global] section in config.ini")

    return {
        "WEB_CLIENT_PORT": config.get("WebClient", "WEB_CLIENT_PORT"),
        "WEB_CLIENT_DOCKER_PORT": config.get("WebClient", "WEB_CLIENT_DOCKER_PORT"),
        "APP_SERVER_PORT": config.get("AppService", "APP_SERVER_PORT"),
        "APP_SERVER_DOCKER_PORT": config.get("AppService", "APP_SERVER_DOCKER_PORT"),
        "CONTAINER_PREFIX": config.get("Global", "CONTAINER_PREFIX"),  # Get container prefix from [Global] section
    }

def read_db_config(instance_path):
    """Read db_config.ini inside each instance directory."""
    db_config_path = os.path.join(instance_path, "db_config.ini")
    config = configparser.ConfigParser()
    config.read(db_config_path)

    if "database" not in config:
        raise ValueError(f"Missing [database] section in {db_config_path}")

    return {
        "ROOT_PASSWORD": config.get("database", "ROOT_PASSWORD"),
        "HOST_PORT": config.get("database", "HOST_PORT"),
    }

def generate_docker_compose(parent_dir):
    """Generate the docker-compose.yml file dynamically."""
    db_instances = get_db_instances(parent_dir)
    config_values = read_config(os.path.join(parent_dir, "config.ini"))
    container_prefix = config_values["CONTAINER_PREFIX"]

    compose_dict = {
        "services": {},
        "volumes": {}
    }

    # Add database services
    for instance in db_instances:
        instance_path = os.path.join(parent_dir, "db_instances", instance)
        db_values = read_db_config(instance_path)
        
        # Add database service with config volume
        compose_dict["services"][f"{instance}_db"] = {
            "build": f"./db_instances/{instance}",
            "container_name": f"{container_prefix}_{instance}_db_container",  # Apply prefix
            "restart": "always",
            "environment": {
                "MYSQL_ROOT_PASSWORD": db_values["ROOT_PASSWORD"]
            },
            "ports": [f'{db_values["HOST_PORT"]}:3306'],
            "volumes": [
                f"{instance}_data:/var/lib/mysql",
                f"{instance}_configs:/etc/mysql/configs"  # Add config volume here
            ]
        }

        compose_dict["volumes"][f"{instance}_data"] = {}
        compose_dict["volumes"][f"{instance}_configs"] = {}

    # Add AppService
    compose_dict["services"]["appservice"] = {
        "build": "./application/appservice",
        "container_name": f"{container_prefix}_appservice_container",  # Apply prefix
        "restart": "always",
        "depends_on": [f"{instance}_db" for instance in db_instances],
        "environment": {f"{instance}_host": f"{instance}_db" for instance in db_instances},
        "ports": [f"{config_values['APP_SERVER_PORT']}:{config_values['APP_SERVER_DOCKER_PORT']}"],  # Ports without quotes
        "volumes": [
            "appservice_logs:/app/Logs",
            *[f"{instance}_configs:/app/configs/{instance.lower()}" for instance in db_instances]  # Mounting AMS/BMS configs here
        ]
    }
    
    compose_dict["volumes"][f"appservice_logs"] = {}

    # Add WebClient
    compose_dict["services"]["webclient"] = {
        "build": "./application/webclient",
        "container_name": f"{container_prefix}_webclient_container",  # Apply prefix
        "restart": "always",
        "depends_on": ["appservice"],
        "ports": [f"{config_values['WEB_CLIENT_PORT']}:{config_values['WEB_CLIENT_DOCKER_PORT']}"],  # Ports without quotes
        "environment": [
            "HTTPS=true",
            "SSL_CERT_PATH=/etc/ssl/certs/webclient/server.crt",
            "SSL_KEY_PATH=/etc/ssl/certs/webclient/server.key"
        ]
    }

    # Define the output file path
    output_file = os.path.join(parent_dir, "docker-compose.yml")

    # Check if the file already exists
    if os.path.exists(output_file):
        print("docker-compose.yml already exists. Skipping file creation.")
        return

    # Write to the YAML file with the desired formatting
    with open(output_file, "w") as f:
        yaml.dump(compose_dict, f, default_flow_style=False, sort_keys=False, indent=4, line_break="\n")

    print("docker-compose.yml file has been created successfully.")

if __name__ == "__main__":
    parent_directory = get_parent_directory()
    generate_docker_compose(parent_directory)
