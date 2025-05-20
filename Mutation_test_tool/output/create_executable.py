from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Add the file path to the search path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..', 'assets', 'docs'))
sys.path.append(parent_dir)

# Import the module
from build_documentation import build_documentation

# Get the current working directory (one level above the script directory)
app_main_path = Path(__file__).resolve().parent.parent

# Path to the Markdown file
build_documentation(app_main_path / "assets" / "docs")

# Define variables for each option
confirm_option = "--noconfirm"
deploy_file_option = "--onefile"
console_option = "--windowed"
icon_path = str(app_main_path / "assets" / "img" / "Logo.ico")
app_name = "vNP_ConfigTool"
add_data = str(app_main_path / "assets") + ";assets/"
script_path = str(app_main_path / "vnp_config_tool.py")

# Update asset/utilities by copy files from other apps
 # vnp_fmu_updater
dest_path = app_main_path / "assets" / "utilities"
fmu_updater_file_path = app_main_path.parent / "vnp_fmu_updater" / "output" / "dist" / "vNP_FMU_Updater.exe"
if fmu_updater_file_path.is_file():
    fmu_updater_file_path_copy = dest_path / fmu_updater_file_path.name
    shutil.copy(fmu_updater_file_path, fmu_updater_file_path_copy)

version_file = app_main_path.parent.parent / "VERSION.txt"
if version_file.is_file():
    version_file_copy = dest_path / version_file.name
    shutil.copy(version_file, version_file_copy)

    # Open Version File and update the default json

    # Open Version File and update the default json
    with open(version_file_copy, 'r') as version_file:
        # Get the string from the Version file
        version_content = version_file.read().strip()

    # Load the default json and Update the json_cfg["General"]["Version"] and save it back
    # Load the default JSON
    default_json_path = str(app_main_path / "assets" / "default" / "PS_Default.json")
    with open(default_json_path, 'r') as json_file:
        json_cfg = json.load(json_file)

    # Update the JSON configuration
    json_cfg["General"]["Version"] = "v" + version_content

    # Save the updated JSON back to the file
    with open(default_json_path, 'w') as json_file:
        json.dump(json_cfg, json_file, indent=4)
        json_file.write('\n')

# Construct the command list
command = [
    "pyinstaller",
    confirm_option,
    deploy_file_option,
    console_option,
    f"--icon={icon_path}",
    f"--name={app_name}",
    f"--add-data={add_data}",
    script_path,
]

# Change the directory and run the command
try:
    subprocess.run(command, cwd=app_main_path / "output")
except Exception as e:
    print(e)
    print("Failed to create the executable. Please check the error message above.")
    sys.exit(1)

# Clean Up

# Remove the spec file
os.remove(app_main_path / "output" / "vNP_ConfigTool.spec")

# Remove the build directory
shutil.rmtree(app_main_path / "output" / "build")
