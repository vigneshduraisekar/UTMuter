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

import tkinter as tk

import customtkinter as ctk
import re
import os
from pathlib import Path
from src.utilities.messagebox_helper import SimpleErrorMessage
from src.utilities.messagebox_helper import SimpleWarnMessage
from src.utilities.validation_helper import validate_folder
from src.utilities.widget_helper import FolderEntry
from src.utilities.widget_helper import StringEntry
from src.utilities.widget_helper import ToolTip
from src.utilities.widget_helper import WidgetLabel

####################################################################################################
# Main Setup Function                                                                              #
####################################################################################################
def setup_general_tab(app):
    """Set up the general tab with sub-panels"""
    # Create General Tab
    # ********************************************************************************
    app.general_tab = app.tabv_main.add("General".center(40))
    app.general_tab.configure(border_width=1)
    app.general_tab.grid_columnconfigure(0, weight=1)
    app.general_tab.grid_rowconfigure((0,1,2,3,4,5,6,7,8,9,10,11,12), weight=0)
    # app.general_tab.grid_rowconfigure(4, weight=1)

    # Create Sub Panels
    # ********************************************************************************
    add_general_panel(app)
    add_generatemutant_panel(app)
    logging_panel(app)
    gen_testsuite(app)

# Create General Panel
####################################################################################################
def add_general_panel(app):
    """Set up sub-panel for general configuration"""
    general_label = ctk.CTkLabel(
        app.general_tab, text=" Path configuration",
        anchor=tk.W, bg_color=app.header_color,
        font=ctk.CTkFont("@Bosch Sans Global", 14, weight="normal"),
    )
    general_label.grid(row=0, column=0, sticky=tk.EW)

    general_panel = ctk.CTkFrame(app.general_tab)
    general_panel.grid(row=1, column=0, pady=(0,5), sticky=tk.NSEW)

    # Configure the grid to use all available space for column 1 (entries)
    general_panel.columnconfigure(1, weight=1)


    # Workspace Path Widget
    # ********************************************************************************
    WidgetLabel(
        general_panel, text="Workspace Path:", row=0, column=0,
        tooltip="Enter Workspace Path [string] avoid special characters",
    )

    app.workspace_entry = FolderEntry(
        app, general_panel, placeholder="Enter Workspace Path... --> Click select Button",
        row=0, column=1, columnspan=4, description="Workspace Path Entry",
        tooltip="Enter Workspace Path [string] avoid special characters",
    )

    workspace_button = ctk.CTkButton(general_panel, text="select")
    workspace_button.configure(command=lambda: select_path(app, app.workspace_entry))
    workspace_button.grid(row=0, column=5, padx=5, pady=5, sticky=tk.EW)

    # C file Path Widget
    # ********************************************************************************
    WidgetLabel(
        general_panel, text="Select source file:", row=3, column=0,
        tooltip="Enter source file path [string] avoid special characters",
    )

    # app.cfile_entry = FolderEntry(
    #     app, general_panel, placeholder="Enter source file Path... --> Click select Button",
    #     row=3, column=1, columnspan=4, description="Workspace Path Entry",
    #     tooltip="Enter source file Path [string] avoid special characters",
    # )
    app.cfile_entry = ctk.CTkEntry(general_panel, placeholder_text="Enter Source File Path... --> Click select Button")
    app.cfile_entry.bind("<Return>", lambda event: app.window.focus_set())
    app.cfile_entry.configure(validate="focusout", validatecommand=lambda: validate_file(app, app.cfile_entry.get()))
    app.cfile_entry.grid(columnspan=4, row=3, column=1, padx=5, pady=5, sticky=tk.EW)
    ToolTip(app.cfile_entry, "Enter Source File Path [string] avoid special characters")

    cfile_button = ctk.CTkButton(general_panel, text="select")
    cfile_button.configure(command=lambda: select_file(app, app.cfile_entry))
    cfile_button.grid(row=3, column=5, padx=5, pady=5, sticky=tk.EW)

# Create Mutant generation Panel
####################################################################################################
def add_generatemutant_panel(app):
    """Set up sub-panel for general configuration"""
    generatemutant_label = ctk.CTkLabel(
        app.general_tab, text=" Generate and Execute Mutants",
        anchor=tk.W, bg_color=app.header_color,
        font=ctk.CTkFont("@Bosch Sans Global", 14, weight="normal"),
    )
    generatemutant_label.grid(row=3, column=0, sticky=tk.EW)

    generatemutant_panel = ctk.CTkFrame(app.general_tab)
    generatemutant_panel.grid(row=4, column=0, pady=(0,5), sticky=tk.NSEW)

    # Configure the grid to use all available space for column 1 (entries)
    generatemutant_panel.grid_columnconfigure((0,1,2,3), weight=1)
    generatemutant_panel.grid_rowconfigure((0,1), weight=0)
    generatemutant_panel.grid_rowconfigure(2, weight=1)

     # Mutants Type Widget
    # ********************************************************************************
    WidgetLabel(
        generatemutant_panel, text="Function name:", anchor=tk.E, row=0, column=0,
        tooltip="Select Function for which code to be generated",
    )


    app.function_option = ctk.CTkOptionMenu(
        generatemutant_panel,
        values=["All"])

    app.function_option.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
    ToolTip(app.function_option, "Select function for which code to be generated")

    #Select the Mutant type
    WidgetLabel(
        generatemutant_panel, text="Mutant Type:", anchor=tk.E, row=0, column=2,
        tooltip="Select function for which code to be generated",
    )

    app.mutant_type_option = ctk.CTkOptionMenu(
        generatemutant_panel,
        values=["All","Relational Operator", "Logical Operator", "Arithmetic Operator", "Off by One error", "Return value Change", "Assignment error",
                "Break semantics", "Control Flow Alteration", "Value change", "Wrong Variable Use", "Pointer Arithmetic", "Null Bugs"])
    app.mutant_type_option.grid(row=0, column=3, padx=5, pady=5, sticky=tk.EW)
    ToolTip(app.mutant_type_option, "Select Mutant type for which code to be generated")

    Gen_button = ctk.CTkButton(generatemutant_panel, text="Generate Mutant")
    Gen_button.configure(command=lambda: select_path(app, app.cfile_entry))
    Gen_button.grid(row=0, column=4, padx=5, pady=5, sticky=tk.EW)

     # Mutants test execution Widget
    # ********************************************************************************

    WidgetLabel(
        generatemutant_panel, text="Function name:", anchor=tk.E, row=1, column=0,
        tooltip="Select Function  for which code to be generated",
    )

    app.fctn_option = ctk.CTkOptionMenu(
        generatemutant_panel,
        values=["All"])
    
    app.fctn_option.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
    ToolTip(app.fctn_option, "Select Function for which code to be generated")

    WidgetLabel(
        generatemutant_panel, text="Mutant Type:", anchor=tk.E, row=1, column=2,
        tooltip="Select Mutant type for which code to be generated",
    )

    app.mutanttype_option = ctk.CTkOptionMenu(
        generatemutant_panel,
        values=["All","Relational Operator", "Logical Operator", "Arithmetic Operator", "Off by One error", "Return value Change", "Assignment error",
                "Break semantics", "Control Flow Alteration", "Value change", "Wrong Variable Use", "Pointer Arithmetic", "Null Bugs"])
    app.mutanttype_option.grid(row=1, column=3, padx=5, pady=5, sticky=tk.EW)
    ToolTip(app.mutanttype_option, "Select Mutant type for which code to be generated")

    Execute_button = ctk.CTkButton(generatemutant_panel, text="Execute Test Suite")
    Execute_button.configure(command=lambda: select_path(app, app.cfile_entry))
    Execute_button.grid(row=1, column=4, padx=5, pady=5, sticky=tk.EW)

# Create Logging Panel
####################################################################################################
def logging_panel(app):
    """Set up sub-panel for general configuration"""
    log_label = ctk.CTkLabel(
        app.general_tab, text=" Test results info",
        anchor=tk.W, bg_color=app.header_color,
        font=ctk.CTkFont("@Bosch Sans Global", 14, weight="normal"),
    )
    log_label.grid(row=8, column=0, sticky=tk.EW)

    log_label = ctk.CTkFrame(app.general_tab)
    log_label.grid(row=9, column=0, pady=(0,5), sticky=tk.NSEW)

    # Configure the grid to use all available space for column 1 (entries)
    log_label.grid_columnconfigure((0,1,2,3), weight=1)
    log_label.grid_rowconfigure((0,1), weight=0)
    log_label.grid_rowconfigure(2, weight=1)

    # Live Mutant count
    # ********************************************************************************
    WidgetLabel(
        log_label, text="Live Mutants count:", anchor=tk.E, row=0, column=0,
        tooltip="Count of live mutants after test execution",
    )

    app.livemutant = ctk.CTkEntry(log_label, placeholder_text="count value...")
    app.livemutant.bind("<Return>", lambda event: app.window.focus_set())
    app.livemutant.configure(validate="focusout", validatecommand=lambda: validate_int(app, app.livemutant))
    app.livemutant.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
    ToolTip(app.livemutant, "Count of live mutants after test execution")

    # Killed Mutant count
    # ********************************************************************************
    WidgetLabel(
        log_label, text="Killed Mutants count:", anchor=tk.E, row=1, column=0,
        tooltip="Count of Killed mutants after test execution",
    )

    app.killedmutant = ctk.CTkEntry(log_label, placeholder_text="count value...")
    app.killedmutant.bind("<Return>", lambda event: app.window.focus_set())
    app.killedmutant.configure(validate="focusout", validatecommand=lambda: validate_int(app, app.killedmutant))
    app.killedmutant.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
    ToolTip(app.killedmutant, "Count of Killed mutants after test execution")

    # Score count
    # ********************************************************************************
    WidgetLabel(
        log_label, text="Mutation score:", anchor=tk.E, row=2, column=0,
        tooltip="Mutation score after test execution",
    )

    app.killedmutant = ctk.CTkEntry(log_label, placeholder_text="score value...")
    app.killedmutant.bind("<Return>", lambda event: app.window.focus_set())
    app.killedmutant.configure(validate="focusout", validatecommand=lambda: validate_int(app, app.killedmutant))
    app.killedmutant.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
    ToolTip(app.killedmutant, "Mutation score after test execution")


    openlog_button = ctk.CTkButton(log_label, text="Open log file")
    openlog_button.configure(command=lambda: select_path(app, app.cfile_entry))
    openlog_button.grid(row=1, column=2, padx=5, pady=5, sticky=tk.EW)

# Create Logging Panel
####################################################################################################
def gen_testsuite(app):
    """Set up sub-panel for general configuration"""
    gen_testsuite_label = ctk.CTkLabel(
        app.general_tab, text=" Generate new tests and execute",
        anchor=tk.W, bg_color=app.header_color,
        font=ctk.CTkFont("@Bosch Sans Global", 14, weight="normal"),
    )
    gen_testsuite_label.grid(row=11, column=0, sticky=tk.EW)

    gen_testsuite_label = ctk.CTkFrame(app.general_tab)
    gen_testsuite_label.grid(row=12, column=0, pady=(0,5), sticky=tk.NSEW)

    # Configure the grid to use all available space for column 1 (entries)
    gen_testsuite_label.grid_columnconfigure((0,1,2,3), weight=1)
    gen_testsuite_label.grid_rowconfigure((0,1), weight=0)
    gen_testsuite_label.grid_rowconfigure(2, weight=1)

    gentest_button = ctk.CTkButton(gen_testsuite_label, text="Generate Test suite")
    gentest_button.configure(command=lambda: select_path(app, app.cfile_entry))
    gentest_button.grid(row=0, column=0, padx=5, pady=5, sticky=tk.EW)

    runnewtest_button = ctk.CTkButton(gen_testsuite_label, text="Execute new tests ")
    runnewtest_button.configure(command=lambda: select_path(app, app.cfile_entry))
    runnewtest_button.grid(row=1, column=0, padx=5, pady=5, sticky=tk.EW)

    runalltest_button = ctk.CTkButton(gen_testsuite_label, text="Execute all tests")
    runalltest_button.configure(command=lambda: select_path(app, app.cfile_entry))
    runalltest_button.grid(row=2, column=0, padx=5, pady=5, sticky=tk.EW)



def validate_int(app, widget):

    number = widget.get()

    try:
        if re.search(r'[^0-9]', number):
            SimpleErrorMessage(
                app.window,
                message='The Number must be an integer.\n\n Please enter a valid integer number',
                title="Integer Value Error!",
            )
            return 2

        number = int(number)

    except ValueError:
        SimpleErrorMessage(
            app.window,
            message='The Number must be an integer.\n\n Please enter a valid integer number',
            title="Float Value Error!",
        )
        return 2

    app.window.focus_set()
    return 0


# Callback Function to switch Panels for different Virtual Bus Types
####################################################################################################
def on_option_change(selected_option,app):
    """Switch the Panel for the selected Virtual Bus Type"""
    a=1
    # if selected_option == "All":


    # elif selected_option == "Relational change":


    # elif selected_option == "Logical change":


    # elif selected_option == "Arithmetic change":


    # elif selected_option == "LayeredStandard":


    # else:
    #     raise ValueError("Unsupported virtual Bus Type")


# Callback Functions to get folder path
####################################################################################################
def select_path(app, target_entry):
    """Open a file dialog to select a folder path and update the target entry."""
    folder_path = tk.filedialog.askdirectory()
    if folder_path:
        old_path = target_entry.get()
        target_entry.delete(0, tk.END)
        target_entry.insert(0, folder_path)
        if validate_folder(app, target_entry) != 0:
            target_entry.delete(0, tk.END)
            target_entry.insert(0, old_path)

def select_file(app, target_entry):
    """Select a CRC/SecOC file and insert it into the target entry"""
    # Define the allowed file extensions
    file_types = (
        ("C files", "*.c"),
        ("C++ files", "*.cpp"),
        ("All files", "*.*"),
    )

    workspace_path = Path(app.workspace_entry.get())

    if workspace_path.exists():
        file_path = tk.filedialog.askopenfilename(initialdir=workspace_path, filetypes=file_types)
    else:
        file_path = tk.filedialog.askopenfilename(filetypes=file_types)

    if file_path:  # If a file is selected
        if validate_file(app, file_path):
            # Delete previous content in target entry
            target_entry.delete(0, tk.END)
            # Insert selected file path into target entry
            target_entry.insert(0, file_path)

# Callback Function to validate the CRC file
####################################################################################################
def validate_file(app, path):
    """Validate the CRC/SecOC file path"""
    allowed_extensions = (".c", ".cpp")
    if path:
        if not (os.path.exists(path) and os.path.isfile(path)):
            # Show a warning message if the file does not exist
            SimpleWarnMessage(app.window, title="File Warning!", message="File does not exist. Please select a valid file.")
            return False
        _, file_extension = os.path.splitext(path)
        if file_extension.lower() not in allowed_extensions:
            # Show a warning message if the file extension is not allowed
            SimpleWarnMessage(app.window, title="File Warning!", message="Invalid file extension. Please select a file with the allowed extension(s). [c, cpp]")
            return False
    function_regex = re.compile(r'^\s*[\w*\[\]]+\s+(\w+)\s*\(.*\)\s*{', re.MULTILINE)

    with open(path, 'r') as file:
        c_code = file.read()
    
    # Find all function names
    function_names = function_regex.findall(c_code)
    function_names.insert(0, "All")  # Optional: insert "All" at the top
    app.function_option.configure(values=function_names)
    app.function_option.set("All")
    app.fctn_option.configure(values=function_names)
    app.fctn_option.set("All")

    return True

def show_scrollable_dropdown(app, values):
    """Show a scrollable dropdown menu in a popup window."""
    popup = ctk.CTkToplevel()
    popup.title("Select Function")
    popup.geometry("300x300")
    popup.grab_set()  # Modal behavior

    frame = tk.Frame(popup)
    frame.pack(fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, selectmode=tk.SINGLE)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=listbox.yview)

    for val in values:
        listbox.insert(tk.END, val)

    def on_select(event=None):
        selected_index = listbox.curselection()
        if selected_index:
            selected = listbox.get(selected_index)
            app.function_option_var.set(selected)
            popup.destroy()

    listbox.bind("<Double-1>", on_select)
