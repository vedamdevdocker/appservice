import os
import configparser
import shutil

# Custom configparser that preserves case and formatting
class CaseInsensitiveConfigParser(configparser.ConfigParser):
    def optionxform(self, optionstr):
        return optionstr  # Preserve case

# Define file paths
GIT_INI_PATH = os.path.join(os.getcwd(), "git.ini")
print(f"Checking for git.ini at: {GIT_INI_PATH}")

# Check if git.ini exists
if not os.path.exists(GIT_INI_PATH):
    print(f"Error: git.ini not found at {GIT_INI_PATH}")
    exit(1)

# Read git.ini
git_config = CaseInsensitiveConfigParser()
git_config.read(GIT_INI_PATH)
print("git.ini loaded successfully.")

# Extract home_dir
if "gitdetails" not in git_config or "home_dir" not in git_config["gitdetails"]:
    print("Error: 'home_dir' not found in [gitdetails] section of git.ini")
    exit(1)

HOME_DIR = os.path.join(os.getcwd(), git_config["gitdetails"]["home_dir"])
print(f"Resolved HOME_DIR: {HOME_DIR}")

# Define config.ini path
CONFIG_INI_PATH = os.path.join(os.getcwd(), "config.ini")
print(f"Checking for config.ini at: {CONFIG_INI_PATH}")

# Check if config.ini exists
if not os.path.exists(CONFIG_INI_PATH):
    print(f"Error: config.ini not found in {os.getcwd()}")
    exit(1)

# Read config.ini
config_ini = CaseInsensitiveConfigParser()
config_ini.read(CONFIG_INI_PATH)
print("config.ini loaded successfully.")

# Mappings from git.ini to config.ini
mappings = {
    "gitdetails": {
        "home_dir": [["Global", "company_folder"], ["Global", "CONTAINER_PREFIX"]],
        "git_user": ["gitcreds", "git_user"],
        "git_password": ["gitcreds", "git_password"],
        "git_clone_type": ["gitcreds", "git_clone_type"],
        "webclient_rep": ["gitcreds", "frontend_rep"],
        "appservice_rep": ["gitcreds", "backend_rep"],
    },
    "communication": {
        "email_id": ["communication", "email"],
        "sms_id": ["communication", "sms"],
    },
    "other": {
        "instances": ["instances", "instances"],
        "ports": ["instances", "ports"],
        "INSTANCE_NAMES": ["instances", "INSTANCE_NAMES"],
        "SEED_DATA": ["instances", "SEED_DATA"],
        "APP_SERVER_HOST": ["AppService", "APP_SERVER_HOST"],
        "APP_SERVER_PORT": ["AppService", "APP_SERVER_PORT"],
        "APP_SERVER_DOCKER_PORT": ["AppService", "APP_SERVER_DOCKER_PORT"],
        "APP_BACKEND_ENV_TYPE": ["AppService", "APP_BACKEND_ENV_TYPE"],
        "WEB_CLIENT_APPLICATION_NAME": ["WebClient", "WEB_CLIENT_APPLICATION_NAME"],
        "WEB_CLIENT_APPLICATION_LEVEL": ["WebClient", "WEB_CLIENT_APPLICATION_LEVEL"],
        "WEB_CLIENT_PORT": ["WebClient", "WEB_CLIENT_PORT"],
        "WEB_CLIENT_DOCKER_PORT": ["WebClient", "WEB_CLIENT_DOCKER_PORT"],
        "SMTP_HOST": ["SMTP", "SMTP_HOST"],
        "SMTP_PORT": ["SMTP", "SMTP_PORT"],
    },
}

# Update values in config.ini
for section, keys in mappings.items():
    if section in git_config:
        for git_key, config_entries in keys.items():
            if git_key in git_config[section]:
                # Ensure config_entries is treated as a list of lists
                if not isinstance(config_entries[0], list):
                    config_entries = [config_entries]

                for config_section, config_key in config_entries:
                    if config_section in config_ini:
                        print(f"Updating [{config_section}] {config_key} with value from [{section}] {git_key}")
                        config_ini.set(config_section, config_key, git_config[section][git_key])
                    else:
                        print(f"Warning: Section [{config_section}] not found in config.ini, skipping {config_key}...")

# Update CERTIFICATES section
if "CERTIFICATES" in git_config:
    if "CERTIFICATES" not in config_ini:
        print("Adding CERTIFICATES section to config.ini")
        config_ini.add_section("CERTIFICATES")
    for key, value in git_config["CERTIFICATES"].items():
        print(f"Updating [CERTIFICATES] {key} with value from git.ini")
        config_ini.set("CERTIFICATES", key, value)

# Save updated config.ini
print("Writing updated values to config.ini...")
with open(CONFIG_INI_PATH, "w") as configfile:
    for section in config_ini.sections():
        configfile.write(f"[{section}]\n")
        for key, value in config_ini.items(section, raw=True):
            configfile.write(f"{key}={value}\n")
        configfile.write("\n")

print("config.ini successfully updated with values from git.ini")
