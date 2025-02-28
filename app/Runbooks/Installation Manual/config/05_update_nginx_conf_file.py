import os
import configparser

def get_parent_directory():
    """Find the parent directory of the script."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def read_config(config_path):
    """Read the config.ini file and return values."""
    config = configparser.ConfigParser()
    config.read(config_path)

    if "WebClient" not in config or "AppService" not in config:
        raise ValueError("Missing [WebClient] or [AppService] section in config.ini")

    return {
        "WEB_CLIENT_DOCKER_PORT": config.get("WebClient", "WEB_CLIENT_DOCKER_PORT"),
        "APP_SERVER_DOCKER_PORT": config.get("AppService", "APP_SERVER_DOCKER_PORT"),
    }

def update_nginx_conf(nginx_conf_path, config_values):
    """Update nginx.conf with the correct ports."""
    if not os.path.exists(nginx_conf_path):
        raise FileNotFoundError(f"nginx.conf not found at {nginx_conf_path}")

    # Read the nginx.conf content
    with open(nginx_conf_path, "r") as file:
        nginx_content = file.readlines()

    # Update the lines with new port values
    new_nginx_content = []
    for line in nginx_content:
        if line.strip().startswith("listen") and "ssl;" in line:
            new_nginx_content.append(f"    listen {config_values['WEB_CLIENT_DOCKER_PORT']} ssl;\n")
        elif "proxy_pass https://appservice:" in line:
            new_nginx_content.append(f"        proxy_pass https://appservice:{config_values['APP_SERVER_DOCKER_PORT']}/;\n")
        else:
            new_nginx_content.append(line)

    # Write the updated content back to nginx.conf
    with open(nginx_conf_path, "w") as file:
        file.writelines(new_nginx_content)

    print(f"nginx.conf updated with WEB_CLIENT_DOCKER_PORT={config_values['WEB_CLIENT_DOCKER_PORT']} and APP_SERVER_DOCKER_PORT={config_values['APP_SERVER_DOCKER_PORT']}")

if __name__ == "__main__":
    parent_directory = get_parent_directory()
    config_values = read_config(os.path.join(parent_directory, "config.ini"))

    # Path to nginx.conf
    nginx_conf_path = os.path.join(parent_directory, "application", "webclient", "nginx.conf")
    update_nginx_conf(nginx_conf_path, config_values)