import os
import configparser

def get_parent_directory():
    """Find the parent directory of the script."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def read_config(config_path):
    """Read the config.ini file and return values."""
    config = configparser.ConfigParser()
    config.read(config_path)

    if "WebClient" not in config:
        raise ValueError("Missing [WebClient] section in config.ini")

    return {
        "WEB_CLIENT_DOCKER_PORT": config.get("WebClient", "WEB_CLIENT_DOCKER_PORT"),
    }

def update_expose_port(dockerfile_path, config_values):
    """Update only the EXPOSE port in the webclient Dockerfile."""
    if not os.path.exists(dockerfile_path):
        raise FileNotFoundError(f"Dockerfile not found at {dockerfile_path}")

    # Read the Dockerfile content
    with open(dockerfile_path, "r") as file:
        dockerfile_content = file.readlines()

    # Find and update the EXPOSE line
    for i, line in enumerate(dockerfile_content):
        if line.strip().startswith("EXPOSE"):
            dockerfile_content[i] = f"EXPOSE {config_values['WEB_CLIENT_DOCKER_PORT']}\n"
            break

    # Write the updated content back to the Dockerfile
    with open(dockerfile_path, "w") as file:
        file.writelines(dockerfile_content)

    print(f"Webclient Dockerfile updated with EXPOSE {config_values['WEB_CLIENT_DOCKER_PORT']}.")

if __name__ == "__main__":
    parent_directory = get_parent_directory()
    config_values = read_config(os.path.join(parent_directory, "config.ini"))

    # Update only the EXPOSE port in the webclient Dockerfile
    webclient_dockerfile_path = os.path.join(parent_directory, "application", "webclient", "Dockerfile")
    update_expose_port(webclient_dockerfile_path, config_values)
