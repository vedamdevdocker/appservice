import os
import configparser

# Custom configparser that preserves the case of keys
class CaseInsensitiveConfigParser(configparser.ConfigParser):
    def optionxform(self, optionstr):
        return optionstr  # Preserve case

# Define the file paths
GIT_INI_PATH = os.path.join(os.getcwd(), "git.ini")

# Check if git.ini exists
if not os.path.exists(GIT_INI_PATH):
    print(f"Error: git.ini not found at {GIT_INI_PATH}")
    exit(1)

# Read git.ini with case preservation
git_config = CaseInsensitiveConfigParser()
git_config.read(GIT_INI_PATH)

# Extract home_dir from git.ini
if "gitdetails" not in git_config or "home_dir" not in git_config["gitdetails"]:
    print("Error: 'home_dir' not found in [gitdetails] section of git.ini")
    exit(1)

HOME_DIR = os.path.join(os.getcwd(), git_config["gitdetails"]["home_dir"])

# Check if the home directory exists
if not os.path.exists(HOME_DIR):
    print(f"Error: Directory '{HOME_DIR}' does not exist")
    exit(1)

# Define the config.ini path
CONFIG_INI_PATH = os.path.join(HOME_DIR, "config.ini")

# Check if config.ini exists
if not os.path.exists(CONFIG_INI_PATH):
    print(f"Error: config.ini not found in {HOME_DIR}")
    exit(1)

# Read config.ini with case preservation
config_ini = CaseInsensitiveConfigParser()
config_ini.read(CONFIG_INI_PATH)

# Read values from [other] section of git.ini
if "other" not in git_config:
    print("Error: [other] section not found in git.ini")
    exit(1)

other_config = git_config["other"]

# Update config.ini with values from git.ini's [other] section
for key, value in other_config.items():
    key_found = False
    for section in config_ini.sections():
        if key in config_ini[section]:  # Case-sensitive match
            config_ini.set(section, key, value)
            key_found = True
            break  # Stop searching once the key is found

    if not key_found:
        print(f"Warning: Key '{key}' not found in config.ini, skipping...")

# Save updated config.ini while preserving original format (no spaces around '=')
with open(CONFIG_INI_PATH, "w") as configfile:
    for section in config_ini.sections():
        configfile.write(f"[{section}]\n")
        for key, value in config_ini.items(section, raw=True):  # raw=True prevents interpolation
            configfile.write(f"{key}={value}\n")  # No extra spaces around '='
        configfile.write("\n")  # Add a blank line after each section

print(f"config.ini successfully updated with values from git.ini")
