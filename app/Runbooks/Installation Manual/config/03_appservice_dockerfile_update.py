import os
import configparser

def get_parent_directory():
    """Find the parent directory of the script."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def read_config(config_path):
    """Read the config.ini file and return values."""
    config = configparser.ConfigParser()
    config.read(config_path)

    if "AppService" not in config:
        raise ValueError("Missing [AppService] section in config.ini")

    return {
        "APP_SERVER_DOCKER_PORT": config.get("AppService", "APP_SERVER_DOCKER_PORT"),
    }

def update_dockerfile(parent_dir, config_values):
    """Update the Dockerfile inside the appservice directory with the correct exposed port and CMD gunicorn port."""
    appservice_dir = os.path.join(parent_dir, "application", "appservice")
    dockerfile_path = os.path.join(appservice_dir, "Dockerfile")
    
    if not os.path.exists(dockerfile_path):
        raise FileNotFoundError(f"Dockerfile not found in {appservice_dir}")

    # Read the Dockerfile content
    with open(dockerfile_path, "r") as file:
        dockerfile_content = file.readlines()

    # Update both EXPOSE and CMD gunicorn lines
    new_dockerfile_content = []
    for line in dockerfile_content:
        if line.strip().startswith("EXPOSE"):
            new_dockerfile_content.append(f"EXPOSE {config_values['APP_SERVER_DOCKER_PORT']}\n")
        elif line.strip().startswith('CMD ["gunicorn"'):
            new_dockerfile_content.append(
                f'CMD ["gunicorn", "-b", "0.0.0.0:{config_values["APP_SERVER_DOCKER_PORT"]}", '
                f'"--certfile=/etc/ssl/certs/appservice.crt", '
                f'"--keyfile=/etc/ssl/private/appservice.key", "app:app"]\n'
            )
        else:
            new_dockerfile_content.append(line)

    # Write the updated content back to the Dockerfile
    with open(dockerfile_path, "w") as file:
        file.writelines(new_dockerfile_content)

    print(f"Dockerfile updated with EXPOSE {config_values['APP_SERVER_DOCKER_PORT']} and CMD gunicorn port.")

if __name__ == "__main__":
    parent_directory = get_parent_directory()
    config_values = read_config(os.path.join(parent_directory, "config.ini"))
    update_dockerfile(parent_directory, config_values)
