import os
import configparser
import shutil

def read_config(config_path):
    print("Reading config from:", config_path)  # Debug print to check the path
    config = configparser.ConfigParser()
    config.read(config_path)
    print("Available sections:", config.sections())  # This will print the available sections
    if 'instances' not in config.sections():
        raise ValueError("The 'instances' section is missing in the config file.")
    return config


def validate_config(config):
    instances = int(config.get("instances", "instances", fallback=0))
    instance_names = config.get("instances", "INSTANCE_NAMES", fallback="").split(",")
    ports = config.get("instances", "ports", fallback="").split(",")
    
    if instances != len(instance_names) - 1:
        raise ValueError("Mismatch between instances count and INSTANCE_NAMES list")
    if instances != len(ports) - 1:
        raise ValueError("Mismatch between instances count and ports list")
    
    return instance_names, ports

def create_instance_directories(base_dir, instance_names):
    for instance in instance_names:
        instance_cleaned = instance.strip()  # Remove leading and trailing spaces
        instance_path = os.path.join(base_dir, instance_cleaned.lower())  # Convert to lowercase
        os.makedirs(instance_path, exist_ok=True)

def create_db_config(instance_path, instance, port, config):
    db_config_path = os.path.join(instance_path, "db_config.ini")
    
    # Only create the file if it doesn't exist
    if os.path.exists(db_config_path):
        return  # Do not overwrite the existing file
    
    print(f"Creating db_config.ini for {instance} with HOST_PORT={port}")

    # Update the host to use the instance parameter
    config_content = f"""[database]
host={instance}_db
port=3306
user={instance.lower()}_usr0
password={config.get('instances', 'USER_PASSWORD')}
ROOT_PASSWORD={config.get('instances', 'ROOT_PASSWORD')}
HOST_PORT={port}
"""

    # Write with LF line endings
    with open(db_config_path, "w", newline="\n") as f:
        f.write(config_content)

    # Set permissions to read/write for owner and read for others (644)
    os.chmod(db_config_path, 0o644)

def create_sql_script(instance_path, instance, config):
    sql_script_path = os.path.join(instance_path, "create_user.sql")
    
    # Only create the script if it doesn't exist
    if os.path.exists(sql_script_path):
        return  # Do not overwrite the existing file

    # Directly retrieve the user and password from the config file
    username = f"{instance.lower()}_usr0"
    password = config.get("instances", "USER_PASSWORD")
    
    with open(sql_script_path, "w") as f:
        f.write(f"CREATE USER '{username}'@'%' IDENTIFIED BY '{password}';\n")
        f.write(f"GRANT ALL PRIVILEGES ON *.* TO '{username}'@'%' WITH GRANT OPTION;\n")
        f.write("FLUSH PRIVILEGES;\n")

def copy_schema_scripts(schema_dir, instance_path):
    scripts_dir = os.path.join(schema_dir, "scripts")
    target_dir = os.path.join(instance_path, "scripts")
    if os.path.exists(scripts_dir):
        shutil.copytree(scripts_dir, target_dir, dirs_exist_ok=True)
        
def create_dockerfile(instance_path):
    dockerfile_path = os.path.join(instance_path, "Dockerfile")
    with open(dockerfile_path, "w") as f:
        f.write("""
# Use official MySQL image as base
FROM mysql:8

# Copy all SQL scripts and subfolders from 'scripts/create' to MySQL initialization directory
COPY scripts/create /docker-entrypoint-initdb.d/
COPY create_user.sql /docker-entrypoint-initdb.d/

# Copy db_config.ini to /etc/mysql/configs/
COPY db_config.ini /etc/mysql/configs/

# Expose MySQL port
EXPOSE 3306
""".strip())

def create_dockerfile_with_seed_data(instance_path):
    dockerfile_path = os.path.join(instance_path, "Dockerfile")
    with open(dockerfile_path, "w") as f:
        f.write("""
# Use official MySQL image as base
FROM mysql:8

# Copy all SQL scripts and subfolders from 'scripts/create' to MySQL initialization directory
COPY scripts/create /docker-entrypoint-initdb.d/
COPY create_user.sql /docker-entrypoint-initdb.d/

# Copy the seed data dump to MySQL initialization directory
COPY scripts/seed_data/seed_data_dump.sql /docker-entrypoint-initdb.d/

# Copy db_config.ini to /etc/mysql/configs/
COPY db_config.ini /etc/mysql/configs/

# Expose MySQL port
EXPOSE 3306
""".strip())

def main():
    # Get the directory of the script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)  # Parent directory of the current script
    
    # Define paths using the parent directory
    config_path = os.path.join(parent_dir, "config.ini")
    db_instances_path = os.path.join(parent_dir, "db_instances")
    schema_path = os.path.join(parent_dir, "config", "schema")
    
    print(f"Config Path: {config_path}")
    print(f"DB Instances Path: {db_instances_path}")
    
    # Ensure the config file exists at the specified location
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found at {config_path}")
    
    config = read_config(config_path)
    instance_names, ports = validate_config(config)  # Get instances and ports list
    
    # Read SEED_DATA values
    seed_data_values = config.get("instances", "SEED_DATA", fallback="").split(",")
    
    if len(instance_names) != len(ports) or len(instance_names) != len(seed_data_values):
        raise ValueError("Mismatch between instance names, ports, and SEED_DATA lists.")
    
    create_instance_directories(db_instances_path, instance_names)
    for instance, port, seed_data in zip(instance_names, ports, seed_data_values):
        instance_cleaned = instance.strip()  # Remove leading and trailing spaces
        seed_data_cleaned = seed_data.strip().lower()  # Convert to lowercase for comparison

        instance_path = os.path.join(db_instances_path, instance_cleaned.lower())  # Convert to lowercase
        create_db_config(instance_path, instance_cleaned.lower(), port, config)  
        create_sql_script(instance_path, instance_cleaned.lower(), config)
        copy_schema_scripts(schema_path, instance_path)

        # Check SEED_DATA value and call the appropriate function
        if seed_data_cleaned == "yes":
            create_dockerfile_with_seed_data(instance_path)
        else:
            create_dockerfile(instance_path)

if __name__ == "__main__":
    main()