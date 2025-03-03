import os
import re

# Define file paths
current_dir = os.path.dirname(os.path.realpath(__file__))
grandparent_dir = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir))

config_file = os.path.join(grandparent_dir, "config.ini")
target_dir = os.path.join(grandparent_dir, "application", "webclient", "my-app", "src", "modules", "admin", "setups")
const_decl_file = os.path.join(target_dir, "ConstDecl.js")

# Ensure config file exists
if not os.path.exists(config_file):
    print(f"❌ ERROR: The file {config_file} does not exist.")
    exit(1)

print(f"✅ Found config file: {config_file}, proceeding...")

# Initialize variables
instance_count = 0
instance_names_list = []
company_value = "Unknown_Company"

# Read config file
with open(config_file, "r") as file:
    current_section = None
    for line in file:
        line = line.strip()
        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1]
        elif "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            if current_section == "instances":
                if key == "instances":
                    try:
                        instance_count = int(value)
                        print(f"🔹 Parsed instance count: {instance_count}")
                    except ValueError:
                        print(f"❌ ERROR: Invalid instance count `{value}` in config.ini")
                        exit(1)
                elif key == "INSTANCE_NAMES":
                    instance_names_list = [name.strip() for name in value.split(",") if name.strip()]
                    print(f"🔹 Parsed instance names: {instance_names_list}")
            elif current_section == "Global" and key == "company_folder":
                company_value = value
                print(f"🔹 Parsed company folder: {company_value}")

# Check required values
if instance_count == 0 or not instance_names_list:
    print("❌ ERROR: No valid instances or instance names found in config.ini.")
    exit(1)

print(f"✅ Successfully parsed {instance_count} instances.")

# Construct ENV_INSTANCES block
instances_block = "export const ENV_INSTANCES = [\n"
for i in range(instance_count + 1):  # FIX: No extra loop iteration
    disname = instance_names_list[i] if i < len(instance_names_list) else f"Unknown_{i}"
    instances_block += f'  {{ instance: "{disname.lower()}", company: "{company_value}", disname: "{disname}", status: "Active", sequence: {i+1} }},\n'
instances_block = instances_block.rstrip(',\n') + "\n];"

print(f"🔹 Updated ENV_INSTANCES:\n{instances_block}")

# Read ConstDecl.js
if not os.path.exists(const_decl_file):
    print(f"❌ ERROR: The file {const_decl_file} does not exist.")
    exit(1)

with open(const_decl_file, 'r') as file:
    content = file.read()

# Remove the existing API_URL definition and replace it with the new one
api_url_pattern = r'export\s+const\s+API_URL\s*=\s*.*?;'
new_api_url_declaration = 'export const API_URL = `${appConfig.appServerProtocol}://${appConfig.appServerHost}:${parseInt(appConfig.appServerPort)}`;\n'

# Replace the existing API_URL with the new one
updated_content = re.sub(api_url_pattern, new_api_url_declaration, content)

# Debugging: Check if API_URL was replaced
if re.search(api_url_pattern, updated_content):
    print("✅ API_URL was updated successfully.")
else:
    print("❌ ERROR: API_URL not replaced.")

# Fix ENV_INSTANCES regex to handle multi-line cases
env_instances_pattern = r'export\s+const\s+ENV_INSTANCES\s*=\s*\[.*?\];'
if not re.search(env_instances_pattern, updated_content, flags=re.DOTALL):
    print("❌ ERROR: ENV_INSTANCES block not found in ConstDecl.js.")
    exit(1)

# Replace ENV_INSTANCES block
updated_content = re.sub(env_instances_pattern, instances_block, updated_content, flags=re.DOTALL)

# Write back to ConstDecl.js
with open(const_decl_file, 'w') as file:
    file.write(updated_content)

print("✅ Successfully updated ConstDecl.js with new API_URL and ENV_INSTANCES!")
