import os
import re

# Define file paths
current_dir = os.path.dirname(os.path.realpath(__file__))

# Target directory and file
grandparent_dir = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir))
config_file = os.path.join(grandparent_dir, "config.ini")  # Updated file name
target_dir = os.path.join(grandparent_dir, "application", "webclient", "my-app", "src", "modules", "admin", "setups")
const_decl_file = os.path.join(target_dir, "ConstDecl.js")

# Ensure config file exists
if not os.path.exists(config_file):
    print(f"ERROR: The {config_file} file does not exist.")
    exit(1)

print(f"{config_file} file found. Proceeding with parsing...")

# Initialize variables
instance_count = 0
instance_names_list = []
company_value = None

# Read config file
with open(config_file, "r") as file:
    current_section = None
    for line in file:
        line = line.strip()
        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1]  # Remove brackets
        elif "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            if current_section == "instances":
                if key == "instances":
                    instance_count = int(value)
                    print(f"DEBUG: Parsed instances count = {instance_count}")  # Debugging
                elif key == "INSTANCE_NAMES":
                    instance_names_list = [name.strip() for name in value.split(",") if name.strip()]
                    print(f"DEBUG: Parsed INSTANCE_NAMES = {instance_names_list}")  # Debugging
            elif current_section == "Global" and key == "company_folder":
                company_value = value
                print(f"DEBUG: Parsed company_folder = {company_value}")  # Debugging

# Ensure defaults are set if missing
if not company_value:
    company_value = "Unknown_Company"

if instance_count == 0 or not instance_names_list:
    print("ERROR: No valid instances or instance names found.")
    exit(1)

print(f"Successfully parsed {instance_count} instances with {len(instance_names_list)} names.")

# Construct the INSTANCES_BLOCK with correct 'disname' values
instances_block = "export const ENV_INSTANCES = [\n"
for i in range(instance_count + 1):  # Adding 1 because `instances=2` means 3 rows
    disname = instance_names_list[i] if i < len(instance_names_list) else "Unknown"
    instances_block += f'  {{ instance: "{disname.lower()}", company: "{company_value}", disname: "{disname}", status: "Active", sequence: {i+1} }},\n'
instances_block = instances_block.rstrip(',\n') + "\n];"

print(f"INSTANCES BLOCK:\n{instances_block}")  # Debugging output

# Read the content of the ConstDecl.js file
if not os.path.exists(const_decl_file):
    print(f"ERROR: The file {const_decl_file} does not exist.")
    exit(1)

with open(const_decl_file, 'r') as file:
    content = file.read()

# Ensure the regex correctly matches the ENV_INSTANCES block
regex_pattern = r'export const ENV_INSTANCES = \[.*?\];'
if not re.search(regex_pattern, content, flags=re.DOTALL):
    print("ERROR: ENV_INSTANCES block not found in ConstDecl.js. No changes made.")
    exit(1)

# Replace the ENV_INSTANCES block safely
updated_content = re.sub(regex_pattern, instances_block, content, flags=re.DOTALL)

# Write the updated content back to the ConstDecl.js file
with open(const_decl_file, 'w') as file:
    file.write(updated_content)

print("✅ ENV_INSTANCES updated successfully!")
