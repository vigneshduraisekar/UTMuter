"""
 **************************************************************************************************
 *
 * COPYRIGHT RESERVED, Robert Bosch GmbH, 2024. All rights reserved.
 * The reproduction, distribution and utilization of this document
 * as well as the communication of its contents to others without
 * explicit authorization is prohibited. Offenders will be held liable for the payment of damages.
 * All rights reserved in the event of the grant of a patent, utility model or design.
 *
 **************************************************************************************************
"""
# pylint: disable=C0301
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tkinter as tk
import webbrowser
from pathlib import Path

from CTkMenuBar import CTkMenuBar
from CTkMenuBar import CustomDropdownMenu
from CTkMessagebox import CTkMessagebox
from lxml import etree as ET



from src.utilities.messagebox_helper import SimpleErrorMessage,SimpleInfoMessage
from src.utilities.messagebox_helper import SimpleSuccessMessage


def setup_menu(app):
    app.menu_main = CTkMenuBar(master=app.window, padx=8)

    app.menu_file = app.menu_main.add_cascade("File", border_width=0)
    app.menu_file_dopdown = setup_file_menu(app)

    app.menu_options = app.menu_main.add_cascade(text="Option", border_width=0)
    app.menu_options_dopdown = setup_options_menu(app)

    app.menu_info = app.menu_main.add_cascade("Information", border_width=0)
    app.menu_info_dopdown = setup_info_menu(app)

def setup_file_menu(app):
    menu_file_dopdown = CustomDropdownMenu(widget=app.menu_file, corner_radius=4, width=200)

    menu_file_dopdown.add_option(
        option="Load (default)", border_width=0,
        command=lambda: load_json_file(app, load_default=True),
    )

    menu_file_dopdown.add_separator()

    menu_file_dopdown.add_option(
        option="Load (*.json)", border_width=0,
        command=lambda: load_json_file(app, load_default=False),
    )

    menu_file_dopdown.add_separator()

    menu_file_dopdown.add_option(
        option="Dump (*.json)", border_width=0,
        command=lambda: save_json_file(app, file_path = None),
    )

    menu_file_dopdown.add_separator()

    menu_file_dopdown.add_option(
        option="Save Project", border_width=0,
        command=lambda: save_project(app, file_path = None),
    )

    menu_file_dopdown.add_separator()

    menu_file_dopdown.add_option(
        option="Exit", border_width=0,
        command=app.window.destroy,
    )

    return menu_file_dopdown

def setup_options_menu(app):
    menu_options_dopdown = CustomDropdownMenu(widget=app.menu_options, corner_radius=4)
    menu_options_dopdown.add_option(
        option="Enable/Disable Additional Options",
        border_width=0,
        command=lambda:enable_disable_additional_options(app),
    )

    menu_options_dopdown.add_separator()

    menu_options_dopdown.add_option(
        option="Enable/Disable Naming Convention Change",
        border_width=0,
        command=lambda:enable_disable_naming_convention_change(app),
    )

    return menu_options_dopdown

def setup_info_menu(app):
    menu_info_dopdown = CustomDropdownMenu(widget=app.menu_info, corner_radius=4)

    menu_info_dopdown.add_option(
        option="Documentation", border_width=0,
        command=lambda: show_documentation(app),
    )

    menu_info_dopdown.add_separator()

    menu_info_dopdown.add_option(
        option="Show Logs", border_width=0,
        command=lambda: show_logs(app),
    )

    menu_info_dopdown.add_separator()


    menu_info_dopdown.add_option(option="Help", border_width=0, command=lambda: show_help(app))

    menu_info_dopdown.add_separator()

    menu_info_dopdown.add_option(option="About", border_width=0, command=lambda: show_about(app))

    return menu_info_dopdown

def save_project(app, file_path):
    # Check if Workspace exists:
    workspace_path = Path(app.workspace_entry.get())

    if not workspace_path.exists():
        # Check if parent directory exists
        if not workspace_path.parent.exists():
            SimpleErrorMessage(app.window, title="Error", message="Workspace path does not exist, please specify a valid workspace path")
            return

        # Ask user if he wants to create the directory
        msg = CTkMessagebox(
            master=app.window,
            title="Error",
            message="Workspace path does not exist, do you want to create it?",
            icon="cancel",
            option_1="Create Workspace",
            option_2="Cancel",
            border_width=2,
            bg_color="gray80",
            corner_radius=8,
            border_color="black",
        )

        if msg.get() == "Cancel":
            return

        workspace_path.mkdir(parents=True)

    # Save the project
    apps_path = workspace_path / "apps"
    if not apps_path.exists():
        apps_path.mkdir(parents=True)

    if app.gen_pbaas_box.get():
        # Generate Subfolder sources
        sources_path = workspace_path / "sources"
        if not sources_path.exists():
            sources_path.mkdir(parents=True)

    # Check if network file exists and copy it to workspace
    network_file_path = Path(app.net_file_entry.get())
    if network_file_path.exists():
        if app.gen_pbaas_box.get():
            network_file_path_copy = workspace_path / "sources" / network_file_path.name
        else:
            network_file_path_copy = workspace_path / network_file_path.name
        if network_file_path != network_file_path_copy:
            shutil.copy(network_file_path, network_file_path_copy)
    else:
        SimpleErrorMessage(app.window, title="Error", message="Network file does not exist, please specify a valid network file")
        return

    # Check if CRC File exists and copy it to workspace
    crc_file_path = Path(app.crc_file_entry.get())
    if crc_file_path.name in ["dummy", ""]:
        SimpleInfoMessage(app.window, title="Info", message="CRC file is either empty or dummy ")
    elif crc_file_path.is_file():
        if app.gen_pbaas_box.get():
            crc_file_path_copy = workspace_path / "sources" / crc_file_path.name
        else:
            crc_file_path_copy = workspace_path / crc_file_path.name
        if crc_file_path != crc_file_path_copy:
            shutil.copy(crc_file_path, crc_file_path_copy)
    else:
        num_rows = app.pattern_table.grid_size()[1]

        # Iterate over each row
        for row in range(1, num_rows):  # Start from 1 to skip the header row
            function_widget = app.pattern_table.grid_slaves(row=row, column=4)[0]
            if function_widget.get() != "":
                SimpleErrorMessage(app.window, title="Error", message="CRC file does not exist, please specify a valid CRC file")
                return
            
    # Check if SecOC File exists and copy it to workspace
    secoc_file_path = Path(app.secoc_file_entry.get())
    if app.secoc_box.get():
        if secoc_file_path.name in ["dummy", ""]:
            SimpleInfoMessage(app.window, title="Info", message="SecOC file is either empty or dummy ")
        elif secoc_file_path.is_file():
            if app.gen_pbaas_box.get():
                secoc_file_path_copy = workspace_path / "sources" / secoc_file_path.name
            else:
                secoc_file_path_copy = workspace_path / secoc_file_path.name
            if secoc_file_path != secoc_file_path_copy:
                shutil.copy(secoc_file_path, secoc_file_path_copy)
    # else:
    #     num_rows = app.pattern_table.grid_size()[1]

    #     # Iterate over each row
    #     for row in range(1, num_rows):  # Start from 1 to skip the header row
    #         function_widget = app.pattern_table.grid_slaves(row=row, column=4)[0]
    #         if function_widget.get() != "":
    #             SimpleErrorMessage(app.window, title="Error", message="SecOC file does not exist, please specify a valid CRC file")
    #             return

    # Check if fmu_configurator_option is set to Workspace and copy wxe to workspace
    if app.fmu_configurator_option.get() == "Workspace":
        fmu_updater_file_path = Path(app.utilities_path) / "vNP_FMU_Updater.exe"
        if fmu_updater_file_path.is_file():
            fmu_updater_file_path_copy = workspace_path / "apps" / fmu_updater_file_path.name
            shutil.copy(fmu_updater_file_path, fmu_updater_file_path_copy)


    # Save the project file
    # File name shall be the same as the network file name
    project_file_name = network_file_path.name.split(".")[0] + ".json"
    if app.gen_pbaas_box.get():
        project_file_path = workspace_path / "sources" / project_file_name
    else:
        project_file_path = workspace_path / project_file_name

    save_json_file(app, project_file_path)

    # Create the PBAAS Recipe
    if app.gen_pbaas_box.get():
        # Adapt the Normal Recipe
        # *****************************************************************************************
        pbaas_path_pbr = Path(app.utilities_path) / "vNP_FMU_PBAAS.pbr"
        tree = ET.parse(pbaas_path_pbr)
        root = tree.getroot()

        # Update plugin version in the specified group
        for plugin in root.xpath("//group[@name='vNP_Generation']/plugin[@name='integration_vNP/build_vnp_for_sil']"):
            plugin.set('version', "vNPGen_v" + app.app_version)

        # Modify specific parameters
        for param in root.xpath("//param[@name='vNPVersion']"):
            param.text = "v" + app.app_version
        for param in root.xpath("//param[@name='copyvNPSources']"):
            param.text = "false"
        for param in root.xpath("//param[@name='configFileName']"):
            param.text = project_file_path.name
        for param in root.xpath("//param[@name='networkFileName']"):
            param.text = network_file_path.name.split(".")[0]
        for param in root.xpath("//param[@name='extCRCFileName']"):
            param.text = crc_file_path.name
        for param in root.xpath("//param[@name='extSecOCFileName']"):
            param.text = secoc_file_path.name

        # Save the modified XML tree back to the file
        tree.write(workspace_path / "vNP_FMU_PBAAS.pbr", encoding='utf-8', xml_declaration=True)


        # Adapt the Defaults Recipe
        # *****************************************************************************************
        pbaas_path_pbr_default = Path(app.utilities_path) / "vNP_FMU_PBAAS.pbr_defaults"
        tree = ET.parse(pbaas_path_pbr_default)
        root = tree.getroot()

        # Modify specific parameters
        for param in root.xpath("//param[@name='vNPVersion']"):
            param.text = "v" + app.app_version
        for param in root.xpath("//param[@name='copyvNPSources']"):
            param.text = "false"
        for param in root.xpath("//param[@name='configFileName']"):
            param.text = project_file_path.name
        for param in root.xpath("//param[@name='networkFileName']"):
            param.text = network_file_path.name
        for param in root.xpath("//param[@name='extCRCFileName']"):
            param.text = crc_file_path.name
        for param in root.xpath("//param[@name='extSecOCFileName']"):
            param.text = secoc_file_path.name
        for param in root.xpath("//param[@name='FMUName']"):
            param.text = app.fmu_name_entry.get()
        for param in root.xpath("//param[@name='busType']"):
            param.text = app.virtual_bus_type_option.get()
        for param in root.xpath("//param[@name='busProtocol']"):
            param.text = app.protocol_option.get()
        for param in root.xpath("//param[@name='nodeName']"):
            param.text = app.ecu_name_entry.get()

        # Save the modified XML tree back to the file
        tree.write(workspace_path / "vNP_FMU_PBAAS.pbr_defaults", encoding='utf-8', xml_declaration=True)

        # Adapt the metadata.json
        # *****************************************************************************************
        metadata_src_path = Path(app.utilities_path) / "metadata.json"

        with open(metadata_src_path, "r") as f:
            metadata = f.read()

        # Replace the placeholders

        # {FMUName} & {nodeName}
        metadata = metadata.replace("{FMUName}", app.fmu_name_entry.get())
        metadata = metadata.replace("{nodeName}", app.fmu_name_entry.get())

        # {vNPVersion}
        metadata = metadata.replace("{vNPVersion}", "v" + app.app_version)

        # {busProtocol}
        metadata = metadata.replace("{busProtocol}", app.protocol_option.get())

        # {busType}
        metadata = metadata.replace("{busType}", app.virtual_bus_type_option.get())

        # {Bitness}
        bitness = ""
        if "64" in app.os_arch_option.get():
            bitness = "x86_64-" + app.operating_system_option.get().lower()
        else:
            bitness = "x86-" + app.operating_system_option.get().lower()

        metadata = metadata.replace("{Bitness}", bitness)

        metadata_dest_path = workspace_path / "sources" /"metadata.json"
        with open(metadata_dest_path, "w") as f:
            f.write(metadata)

    SimpleSuccessMessage(app.window, title="Save Project", message="Save Project successfully")

def enable_disable_additional_options(app):
    try:
        app.tabv_main.delete("Additional".center(40))
        app.tabv_main.set("General".center(40))
        app.tabv_main._create_tab()
    except Exception as _:
        #setup_additional_tab(app)
        app.tabv_main._name_list.append("Additional".center(40))
        app.tabv_main._tab_dict["Additional".center(40)] = app.additional_tab
        app.tabv_main._segmented_button.insert(4, "Additional".center(40))
        app.tabv_main.set("Additional".center(40))

def enable_disable_naming_convention_change(app):
    if bool(app.name_conv_overview_panel.winfo_ismapped()):
        app.name_conv_overview_panel.grid_forget()
        app.name_conv_change_panel.grid(rowspan=2, row=3, column=0, pady=(0,5), sticky=tk.NSEW)
    else:
        app.name_conv_change_panel.grid_forget()
        app.name_conv_overview_panel.grid(rowspan=2, row=3, column=0, pady=(0,5), sticky=tk.NSEW)

    app.tabv_main.set("General".center(40))
    update_naming_convention_overview(app)

def show_documentation(app):
    docu_link = Path(app.docs_path) / "index.html"
    webbrowser.open_new(docu_link.as_uri())

def show_logs(app):
    log_file = Path(app.logger_path)
    if log_file.exists():
        # Open the file with the default application
        if os.name == 'nt':  # Windows
            os.startfile(log_file)
        elif os.name == 'posix':  # macOS, Linux
            subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', log_file])
    else:
        SimpleErrorMessage(app.window, title="Error", message="Log file does not exist, please specify a valid log file")

def show_help(app):
    msg = CTkMessagebox(
        master=app.window,
        title="Help",
        message=(
                    "vNP is a product from\n"
                    "Robert Bosch GmbH (PS-SC)\n\n"
                    "For support or request, \n"
                    "please contact the vXCU Team\n\n"
                    "Further Information on Docupedia"
        ),
        icon=None,
        justify="center",
        option_1="Close",
        option_2="Docupedia",
        border_width=2,
        bg_color="gray80",
        corner_radius=8,
        border_color="black",
    )

    if msg.get() != "Docupedia":
        return

    webbrowser.open_new("https://inside-docupedia.bosch.com/confluence/display/GSLC/Virtual+Network+Plug")

    app.window.focus_set()

def show_about(app):
    CTkMessagebox(
        master=app.window,
        title="About",
        message=(
                    "vNP Configuration Tool\n"
                    f"      Version v{app.app_version}\n"
                    "    Robert Bosch GmbH"
        ),
        justify="center",
        # wraplength=200,
        icon=None,
        option_1="Close",
        border_width=2,
        bg_color="gray80",
        corner_radius=8,
        border_color="black",
    )
    app.window.focus_set()
