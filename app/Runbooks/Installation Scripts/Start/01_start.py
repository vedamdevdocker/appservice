import os
import sys
import configparser
import shutil
import time
import subprocess

def check_installed(command):
    """Check if a command is available on the system."""
    try:
        subprocess.run([command, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except FileNotFoundError:
        print(f"Error: {command} is not installed. Please install it and try again.")
        sys.exit(1)

def read_git_ini(file_path):
    """Read the git.ini file and return the configuration."""
    if not os.path.exists(file_path):
        print("Error: git.ini file not found in the current directory.")
        sys.exit(1)
    
    config = configparser.ConfigParser()
    config.read(file_path)
    
    try:
        home_dir = config.get("gitdetails", "home_dir").strip()
        appservice_rep = config.get("gitdetails", "appservice_rep").strip()
        webclient_rep = config.get("gitdetails", "webclient_rep").strip()
    except configparser.NoOptionError as e:
        print(f"Error reading git.ini: {e}")
        sys.exit(1)
    
    return home_dir, appservice_rep, webclient_rep

def create_directories(base_dir):
    """Create required directory structure."""
    application_dir = os.path.join(base_dir, "application")
    appservice_dir = os.path.join(application_dir, "appservice")
    webclient_dir = os.path.join(application_dir, "webclient")
    
    for directory in [base_dir, application_dir, appservice_dir, webclient_dir]:
        os.makedirs(directory, exist_ok=True)
    
    return appservice_dir, webclient_dir

def clone_repository(repo_url, target_dir):
    """Clone a Git repository into the specified directory."""
    print(f"Cloning {repo_url} into {target_dir}...")
    subprocess.run(["git", "clone", repo_url, target_dir], check=True)

def copy_installation_scripts(appservice_dir, target_dir):
    """Copy files from 'Installation Scripts' to target directory."""
    installation_scripts_dir = os.path.join(appservice_dir, "app", "Runbooks", "Installation Scripts")
    if not os.path.exists(installation_scripts_dir):
        print("Error: Installation Scripts directory not found.")
        sys.exit(1)
    
    for item in os.listdir(installation_scripts_dir):
        s = os.path.join(installation_scripts_dir, item)
        d = os.path.join(target_dir, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

def main():
    check_installed("git")
    check_installed("docker")
    
    git_ini_path = os.path.join(os.getcwd(), "git.ini")
    home_dir, appservice_rep, webclient_rep = read_git_ini(git_ini_path)
    
    base_dir = os.path.join(os.getcwd(), home_dir)
    appservice_dir, webclient_dir = create_directories(base_dir)
    
    clone_repository(appservice_rep, appservice_dir)
    clone_repository(webclient_rep, webclient_dir)
    
    print("Waiting for cloning to complete...")
    time.sleep(5)
    
    copy_installation_scripts(appservice_dir, base_dir)
    print("Setup completed successfully.")

if __name__ == "__main__":
    main()
