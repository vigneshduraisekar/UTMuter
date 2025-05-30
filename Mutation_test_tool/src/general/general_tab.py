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
from openai import OpenAI

import customtkinter as ctk
import re
import shutil
import subprocess
import os
import time
import json
import threading
import concurrent.futures
from pathlib import Path
from bs4 import BeautifulSoup
from src.utilities.messagebox_helper import SimpleErrorMessage
from src.utilities.messagebox_helper import SimpleSuccessMessage
from src.utilities.messagebox_helper import SimpleWarnMessage
from src.utilities.validation_helper import validate_folder
from src.utilities.widget_helper import FolderEntry
from src.utilities.widget_helper import StringEntry
from src.utilities.widget_helper import ToolTip
from src.utilities.widget_helper import WidgetLabel
from src.utilities.widget_helper import show_progress_popup

USER_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../../user_config.json")

def save_gui_state(app):
    """Save GUI state to JSON file."""
    data = {
        "workspace_folder": app.workspace_entry.get(),
        "last_function": app.function_option.get(),
        "mutant_type": "",  # Add if you have a mutant type option
        "cfile_path": app.cfile_entry.get()
    }
    with open(USER_CONFIG_PATH, "w") as f:
        json.dump(data, f)

def load_gui_state(app):
    """Load GUI state from JSON file."""
    if os.path.exists(USER_CONFIG_PATH):
        with open(USER_CONFIG_PATH, "r") as f:
            try:
                data = json.load(f)
            except Exception:
                return
        # Set values if present
        if "workspace_folder" in data:
            app.workspace_entry.delete(0, tk.END)
            app.workspace_entry.insert(0, data["workspace_folder"])
        if "cfile_path" in data:
            app.cfile_entry.delete(0, tk.END)
            app.cfile_entry.insert(0, data["cfile_path"])
        # Validate file to populate function list
        if "cfile_path" in data and os.path.exists(data["cfile_path"]):
            validate_file(app, data["cfile_path"])
        if "last_function" in data and data["last_function"] in app.function_option.cget("values"):
            app.function_option.set(data["last_function"])
            app.fctn_option.set(data["last_function"])

class llmfarminf():
    def __init__(self, model = "gpt-4o-mini") -> None:
        self.model = model
        self.client = OpenAI(
            api_key="dummy",
            base_url="https://aoai-farm.bosch-temp.com/api/openai/deployments/askbosch-prod-farm-openai-gpt-4o-mini-2024-07-18",
            default_headers = {"genaiplatform-farm-subscription-key": "e51cbe98f0c64e41befc98eb8eca66d9"}
        )

    def _gen_message(self, sysprompt, userprompt):
        return [
            {"role" : "system", "content" : sysprompt},
            {"role" : "user", "content" : userprompt}
        ]

    def _completion(self, usertext, sysprompt):
        messages = self._gen_message(sysprompt, usertext)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            extra_query={"api-version": "2024-08-01-preview"}
        )
        return response.choices[0].message.content

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
    load_gui_state(app)

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
    # WidgetLabel(
    #     generatemutant_panel, text="Mutant Type:", anchor=tk.E, row=0, column=2,
    #     tooltip="Select function for which code to be generated",
    # )

    # app.mutant_type_option = ctk.CTkOptionMenu(
    #     generatemutant_panel,
    #     values=["All","Relational Operator", "Logical Operator", "Arithmetic Operator", "Off by One error", "Return value Change", "Assignment error",
    #             "Break semantics", "Control Flow Alteration", "Value change", "Wrong Variable Use", "Pointer Arithmetic", "Null Bugs"])
    # app.mutant_type_option.grid(row=0, column=3, padx=5, pady=5, sticky=tk.EW)
    # ToolTip(app.mutant_type_option, "Select Mutant type for which code to be generated")

    Gen_button = ctk.CTkButton(generatemutant_panel, text="Generate Mutant")
    Gen_button.configure(command=lambda: gen_mutant(app))
    Gen_button.grid(row=0, column=3, padx=5, pady=5, sticky=tk.EW)

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

    # WidgetLabel(
    #     generatemutant_panel, text="Mutant Type:", anchor=tk.E, row=1, column=2,
    #     tooltip="Select Mutant type for which code to be generated",
    # )

    # app.mutanttype_option = ctk.CTkOptionMenu(
    #     generatemutant_panel,
    #     values=["All","Relational Operator", "Logical Operator", "Arithmetic Operator", "Off by One error", "Return value Change", "Assignment error",
    #             "Break semantics", "Control Flow Alteration", "Value change", "Wrong Variable Use", "Pointer Arithmetic", "Null Bugs"])
    # app.mutanttype_option.grid(row=1, column=3, padx=5, pady=5, sticky=tk.EW)
    # ToolTip(app.mutanttype_option, "Select Mutant type for which code to be generated")

    Execute_button = ctk.CTkButton(generatemutant_panel, text="Execute Test Suite")
    Execute_button.configure(command=lambda: Execute_test(app))
    Execute_button.grid(row=1, column=3, padx=5, pady=5, sticky=tk.EW)

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

    app.mutantscore = ctk.CTkEntry(log_label, placeholder_text="score value...")
    app.mutantscore.bind("<Return>", lambda event: app.window.focus_set())
    app.mutantscore.configure(validate="focusout", validatecommand=lambda: validate_int(app, app.mutantscore))
    app.mutantscore.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
    ToolTip(app.mutantscore, "Mutation score after test execution")

    createlog_button = ctk.CTkButton(log_label, text="Create report file")
    createlog_button.configure(command=lambda: create_log(app))
    createlog_button.grid(row=0, column=2, padx=5, pady=5, sticky=tk.EW)

    calc_score_button = ctk.CTkButton(log_label, text="Calculate mutant score")
    calc_score_button.configure(command=lambda: calc_score(app))
    calc_score_button.grid(row=1, column=2, padx=5, pady=5, sticky=tk.EW)


    openlog_button = ctk.CTkButton(log_label, text="Open Consolidated Report")
    openlog_button.configure(command=lambda: open_log(app))
    openlog_button.grid(row=2, column=2, padx=5, pady=5, sticky=tk.EW)

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

# Callback Functions to get C file name
####################################################################################################
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

# Callback Function to validate the C file and get function name list
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
    if "if" in function_names:
        function_names.remove("if")
    app.function_option.configure(values=function_names)
    app.function_option.set("All")
    app.fctn_option.configure(values=function_names)
    app.fctn_option.set("All")

    return True

# Callback Function to generate mutant and save the c file
####################################################################################################
def gen_mutant(app):
    popup = show_progress_popup(app, "Generating Mutant...")
    def task():
        try:
            c_file_path = app.cfile_entry.get()
            function_name = app.function_option.get()
            if function_name == "All":
                function_list = app.function_option.cget("values")
                total_mutants = 0
                for function_name in function_list[1:]:
                    # Update progress bar message
                    for widget in popup.winfo_children():
                        if isinstance(widget, ctk.CTkLabel):
                            if popup.winfo_exists():
                                widget.configure(text=f"Generating mutant for {function_name}...")
                                popup.update()
                    mutants = prompt_and_gen_mutant(app, function_name, c_file_path, show_message=False)
                    if mutants:
                        total_mutants += len(mutants)
                # Show only one success message at the end
                SimpleSuccessMessage(app.window, title="Generate Mutant window", message=f"Mutants generated for all functions. Total mutants: {total_mutants}")
            else:
                # For individual function, show a popup with the number of mutants generated
                mutants = prompt_and_gen_mutant(app, function_name, c_file_path, show_message=False)
                num_mutants = len(mutants) if mutants else 0
                SimpleSuccessMessage(app.window, title="Generate Mutant window", message=f"{num_mutants} mutants generated for {function_name}")
        finally:
            if popup.winfo_exists():
                app.window.after(0, popup.destroy)
    threading.Thread(target=task).start()

def prompt_and_gen_mutant(app, function_name, c_file_path, show_message=True):
    with open(c_file_path, 'r') as f:
        c_code = f.read()
    c_function_code = extract_function_code(c_code, function_name)

    system_prompt = "You are a programming expert specializing in mutation testing for C code."

    user_prompt = f"""
Given the following C function, analyze the code and identify all potential mutation points where a single operator, logical construct, or assignment can be changed to create a meaningful mutant.

For each mutation point:
1. Generate a mutant by changing ONLY ONE operator or logic at that point (e.g., + to -, == to !=, && to ||, > to >=, etc.).
2. Give each mutant a unique, descriptive name (e.g., Mutant_GreaterToLess, Mutant_AndToOr, Mutant_IncrementToDecrement).
3. Show the complete mutated function as a C code block, with the mutation clearly highlighted or commented (e.g., // MUTATION: changed >= to >).
4. Briefly explain how this mutation changes the function's behavior.

**Guidelines:**
- Only one mutation per mutant.
- Do not change variable names or function signatures.
- Do not introduce syntax errors.
- Do not generate redundant mutants (e.g., do not mutate the same operator in the same way more than once).
- Focus on these mutation types:
    - Arithmetic operators: +, -, *, /, %, ++, --
    - Relational operators: <, <=, >, >=, ==, !=
    - Logical operators: &&, ||, !
    - Assignment operators: =, +=, -=, *=, /=, %=
    - Return value changes (e.g., change return true to return false)
    - Control flow changes (e.g., invert a condition)
    - Off by One error (i < n → i <= n)
    - Break semantics (int x = 1; → int x = 0)
    - Wrong variable use (return x; instead of return y;)
    - Pointer arithmetic (ptr != NULL → ptr == NULL)
    - Null bugs (int *ptr = &value;→ int *ptr = NULL)
- When generating a mutant, only change the specific operator or logic at the mutation point. Do not remove, reorder, or restructure any other part of the function.
- **Do not remove, skip, or omit any if, else if, or else branches from the original function.**
- **Do not remove or move any return statements or code blocks from the original function.**
- **The mutated function must have the same structure, logic, and all branches as the original, except for the single mutation.**
- **Only change the specific operator or logic at the mutation point; all other code, comments, and formatting must remain unchanged.**
- **If you change an operator (e.g., -- to ++), do not remove any other code or branches, and do not change the flow of the function.**
- Always preserve all original control flow (if/else, loops, returns, etc.) and ensure the mutated function is complete and syntactically correct.
- Output the entire mutated function as a C code block.

Original function:
```c
{c_function_code}
"""
    obj = llmfarminf()

    # Get the response
    response = obj._completion(user_prompt, system_prompt)
    # Extract mutants
    mutants = extract_c_blocks(response)
    report = write_and_compile(app, mutants, function_name)
    # if show_message and len(mutants) > 0:
    #     SimpleSuccessMessage(app.window, title="Generate Mutant window", message=f"{len(mutants)} Mutants generated for function {function_name}")
    return mutants

def Execute_test(app):
    app.killedmutant.delete(0, 'end')
    app.livemutant.delete(0, 'end')
    app.mutantscore.delete(0, 'end')
    popup = show_progress_popup(app, "Executing Test Suite...")

    def process_file(file_path, c_file_path, report_src, report_dest):
        with open(c_file_path, 'w') as dest_file, open(file_path, 'r') as src_file:
            content = src_file.read()
            dest_file.write(f"// From file: {os.path.basename(file_path)}\n")
            dest_file.write(content + "\n\n")
        execute_test_cantata_cli(app, os.path.basename(file_path), c_file_path, show_popup=False)
        if os.path.exists(report_src):
            shutil.copyfile(report_src, report_dest)

    def task():
        try:
            c_file_path = app.cfile_entry.get()
            if app.fctn_option.get() == "All":
                folder_path = app.workspace_entry.get()
            else:
                folder_path = os.path.join(app.workspace_entry.get(), app.fctn_option.get())
            if os.path.isdir(folder_path):
                if app.fctn_option.get() == "All":
                    for subfolder in os.listdir(folder_path):
                        subfolder_path = os.path.join(folder_path, subfolder)
                        if os.path.isdir(subfolder_path):
                            for file_name in os.listdir(subfolder_path):
                                if file_name.endswith('.c'):
                                    file_path = os.path.join(subfolder_path, file_name)
                                    cantata_dir = os.path.dirname(c_file_path)
                                    report_src = os.path.join(cantata_dir, 'Cantata', 'tests', 'test_Net_MonitoringClasses', 'test_Net_MonitoringClasses.log')
                                    report_dest = os.path.join(subfolder_path, file_name[:-2] +'test.log')
                                    process_file(file_path, c_file_path, report_src, report_dest)
                else:
                    for file_name in os.listdir(folder_path):
                        if file_name.endswith('.c'):
                            file_path = os.path.join(folder_path, file_name)
                            cantata_dir = os.path.dirname(c_file_path)
                            report_src = os.path.join(cantata_dir, 'Cantata', 'tests', 'test_Net_MonitoringClasses', 'test_Net_MonitoringClasses.log')

                            report_dest = os.path.join(folder_path, file_name[:-2] +'_test.log')
                            process_file(file_path, c_file_path, report_src, report_dest)
            # Show success popup only once after all test cases are executed
            app.window.after(0, lambda: SimpleSuccessMessage(app.window, title="Execute test window", message="All test cases executed successfully."))
        finally:
            if popup.winfo_exists():
                app.window.after(0, popup.destroy)

    threading.Thread(target=task).start()

# Update execute_test_cantata_cli to accept show_popup argument
def execute_test_cantata_cli(app, file_name, c_file_path, show_popup=True):
    def run_cmd_in_window(retry_interval = 5):
        cantata_dir = os.path.dirname(c_file_path)
        test_dir = os.path.join(cantata_dir, 'Cantata', 'tests')
        test_dir = os.path.normpath(test_dir)

        pre_build_command = (
            f"cd {test_dir} && "
            "texec -useEnv:ae.be aeee_pro/2017.1.2 && "
            "make clean && "
            "make all EXECUTE=1 OUTPUT_TO_CONSOLE=1 "
        )
        pre_build_return_code = execute_command(pre_build_command, show_window=True)

        # post_build_commands = (
        #     f"cd {test_dir} && "
        #     "texec -useEnv:ae.be aeee_pro/2017.1.2 && "
        #     r"set WORKSPACE_PATH=%APPDATA%/workspace/BBM/%UBK_PRODUCT%/%UBK_PRODUCT_VERSION%/workspace && "
        #     f"set PROJECT_PATH={test_dir} && "
        #     r"aeee_pro -application com.ipl.products.eclipse.cantpp.cdt.TestReportGenerator -data %WORKSPACE_PATH% %PROJECT_PATH% HTML_DETAILED_REPORT"
        # )
        # post_build_return_code = execute_command(post_build_commands, show_window=True)
        # if post_build_return_code == 0:
        #     a = 1

    run_cmd_in_window()

    # Only show the popup if requested
    if show_popup:
        SimpleSuccessMessage(app.window, title="Execute test window", message=f"Test executed for c file-{file_name} successfully")

def execute_command(command, show_window=False):
    if show_window:
        creationflags = subprocess.CREATE_NEW_CONSOLE
    else:
        creationflags = subprocess.CREATE_NO_WINDOW

    # Run the command with specified creation flags
    process = subprocess.run(['cmd.exe', '/c', command], creationflags=creationflags)
    return process.returncode

def create_log(app):
    popup = show_progress_popup(app, "Executing Test Suite...")
    def task():
        try:
            fields_to_extract = [
            "Summary status",
            "Total number of test cases",
            "Test cases passed",
            "Test cases failed",
            "Checks passed",
            "Checks failed"
            ]

            # Consolidated results list
            consolidated_data = []
            if app.function_option.get() == "All":
                folder_path = app.workspace_entry.get()
            else:
                folder_path = os.path.join(app.workspace_entry.get(), app.function_option.get())
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if file.endswith("test_report.html"):
                        file_path = os.path.join(root, file)
                        with open(file_path, "r", encoding="utf-8") as f:
                            soup = BeautifulSoup(f, "html.parser")

                        # Extract info
                        data = {"File": os.path.relpath(file_path, folder_path)}
                        for row in soup.find_all("tr"):
                            cols = row.find_all(["td", "th"])
                            if len(cols) >= 2:
                                key = cols[0].get_text(strip=True)
                                val = cols[1].get_text(strip=True)
                                if key in fields_to_extract:
                                    data[key] = val
                        consolidated_data.append(data)

            # Generate HTML table
            output_html = "<html><head><title>Consolidated Test Report</title></head><body>"
            output_html += "<h2>Consolidated Test Report</h2><table border='1' cellpadding='5'><tr><th>File</th>"

            # Add headers
            for field in fields_to_extract:
                output_html += f"<th>{field}</th>"
            output_html += "</tr>"

            # Add rows
            for entry in consolidated_data:
                output_html += "<tr>"
                output_html += f"<td>{entry.get('File', '')}</td>"
                for field in fields_to_extract:
                    output_html += f"<td>{entry.get(field, '')}</td>"
                output_html += "</tr>"

            output_html += "</table></body></html>"

            # Save consolidated report
            output_file = os.path.join(folder_path, "consolidated_report.html")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(output_html)

            SimpleSuccessMessage(app.window, title="Generate Report window", message=f"Consolidated report generated for function {app.function_option.get()}")
        finally:
            if popup.winfo_exists():
                app.window.after(0, popup.destroy)
    threading.Thread(target=task).start()

def calc_score(app):
    if app.function_option.get() == "All":
        folder_path = app.workspace_entry.get()
    else:
        folder_path = os.path.join(app.workspace_entry.get(), app.function_option.get())
    file_path = os.path.join(folder_path, "consolidated_report.html")
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the table containing the report
    table = soup.find('table')  # Assuming there's only one table in the HTML

    # Initialize a list to capture the failed test cases from each row
    failed_tests = []
    num_rows = 0

    # Iterate over rows in the table, skipping the header
    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')
        num_rows += 1
        if len(cols) > 0:
            # Assuming "Test cases failed" is the 5th column (0-based index 4)
            test_cases_failed = cols[4].text.strip()
            failed_tests.append(test_cases_failed)

    live_mutant = failed_tests.count('0')
    killed_mutant = len(failed_tests) - live_mutant
    app.killedmutant.delete(0, 'end')
    app.livemutant.delete(0, 'end')
    app.mutantscore.delete(0, 'end')
    app.killedmutant.insert(0, killed_mutant)
    app.livemutant.insert(0, live_mutant)
    score = (killed_mutant/num_rows)*100
    percentage_score = f"{score:.1f}%"
    app.mutantscore.insert(0,percentage_score)

def open_log(app):
    if app.function_option.get() == "All":
        folder_path = app.workspace_entry.get()
    else:
        folder_path = os.path.join(app.workspace_entry.get(), app.function_option.get())
    file_path = os.path.join(folder_path, "consolidated_report.html")

    # Check if the file exists
    if os.path.exists(file_path):
        # Open the file using the default web browser
        os.startfile(file_path)  # This works on Windows to open files with default applications
        print(f"Opened: {file_path}")
    else:
        print(f"File not found: {file_path}")



def extract_function_code(c_code, function_name):
    function_regex = re.compile(
        rf'^\s*[a-zA-Z_]\w*\s+{function_name}\s*\([^)]*\)\s*(?:\n|\r|\r\n|\s)*\{{.*?\}}',
        re.MULTILINE | re.DOTALL
    )
    match = function_regex.search(c_code)
    if match:
        return match.group()
    else:
        return None

def extract_c_blocks(llm_response):
    """
    Extracts all C code blocks from the LLM response.
    Returns a list of (mutant_name, code) tuples.
    """
    mutants = []
    # Updated regex to match names like Mutant_Arithmatic, Mutant_Relational, etc.
    pattern = r'(Mutant_[A-Za-z0-9_]+.*?)(```c(.*?)```)'  # Non-greedy match
    for match in re.finditer(pattern, llm_response, re.DOTALL | re.IGNORECASE):
        header = match.group(1)
        code = match.group(3).strip()
        # Extract mutant name from header
        mutant_name_match = re.search(r'(Mutant_[A-Za-z0-9_]+)', header, re.IGNORECASE)
        mutant_name = mutant_name_match.group(1).lower() if mutant_name_match else "mutant_gpt_mini"
        mutants.append((mutant_name, code))

    return mutants

def write_and_compile(app, mutants, function_name):
    report = []
    full_path = os.path.join(app.workspace_entry.get(), function_name)
    os.makedirs(full_path, exist_ok=True)
    for mutant_name, code in mutants:
        dest_path = os.path.join(full_path, mutant_name + ".c")
        shutil.copyfile(app.cfile_entry.get(), dest_path)
        with open(dest_path, 'r') as file:
            content = file.read()

        modified_content = replace_function_body(content, function_name, code)

        with open(dest_path, 'w') as file:
            file.write(modified_content)

    # if len(mutants)>0:
    #     SimpleSuccessMessage(app.window, title="Generate Mutant window", message=f"{len(mutants)} Mutants generated for function {function_name}")

def replace_function_body(code, func_name, new_function_def):
    pattern = rf'\b\S+\s+{func_name}\s*\([^)]*\)\s*\{{.*?\}}'
    new_code = re.sub(pattern, new_function_def, code, flags=re.DOTALL)
    return new_code

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
            if popup.winfo_exists():
                app.window.after(0, popup.destroy)

    listbox.bind("<Double-1>", on_select)
