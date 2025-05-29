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

    app.killedmutant = ctk.CTkEntry(log_label, placeholder_text="score value...")
    app.killedmutant.bind("<Return>", lambda event: app.window.focus_set())
    app.killedmutant.configure(validate="focusout", validatecommand=lambda: validate_int(app, app.killedmutant))
    app.killedmutant.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
    ToolTip(app.killedmutant, "Mutation score after test execution")

    


    openlog_button = ctk.CTkButton(log_label, text="Open log file")
    openlog_button.configure(command=lambda: open_log(app))
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
    # select_operator = app.mutant_type_option.get()
    function_name = app.function_option.get()
    c_file_path= app.cfile_entry.get()
    if function_name == "All":
        function_list = app.function_option.cget("values")
        #loop thru each function and generate mutant
        for function_name in function_list[1:]:
            prompt_and_gen_mutant(app, function_name, c_file_path)        
    else:
        prompt_and_gen_mutant(app, function_name, c_file_path)


def prompt_and_gen_mutant(app, function_name, c_file_path):
    c_function_code = extract_function_code(c_file_path, function_name)

    system_prompt = "You are a programming expert with focus on mutation testing."
    user_prompt = f"""
    Generate specific mutation variants of this C function by changing ONLY ONE operator at a time.
    For each mutation:
    1. Give it a name (Mutant_falsereturn, Mutant_negative_return etc.)
    2. Show the complete function with the mutation highlighted or commented

    Target all operators for mutation:
    
    generate all potential mutants combination by changing only one at a time

    {c_function_code}
    """
    obj = llmfarminf()

    # Get the response
    response = obj._completion(user_prompt, system_prompt)
    # Extract mutants
    mutants = extract_c_blocks(response)

    # Write  mutants
    report = write_and_compile(app, mutants, function_name)


def Execute_test(app):
    # select_operator = app.mutant_type_option.get()
    c_file_path= app.cfile_entry.get()
    if app.fctn_option.get() == "All":
        folder_path = app.workspace_entry.get()
    else:
        folder_path = os.path.join(app.workspace_entry.get(), app.fctn_option.get())
    if os.path.isdir(folder_path):
        if app.fctn_option.get() == "All":
            #Loop thru each sub folder and replace the c file in WS
            for subfolder in os.listdir(folder_path):
                subfolder_path = os.path.join(folder_path, subfolder)
                # Proceed if the item is a directory
                if os.path.isdir(subfolder_path):
                    # Iterate over each file in the subfolder
                    for file_name in os.listdir(subfolder_path):
                        if file_name.endswith('.c'):
                            file_path = os.path.join(subfolder_path, file_name)
                            # Read the .c file and write it to the destination file
                            with open(c_file_path, 'w') as dest_file:
                                with open(file_path, 'r') as src_file:
                                    content = src_file.read()
                                    dest_file.write(f"// From file: {file_name}\n")
                                    dest_file.write(content + "\n\n")
                            execute_test_cantata_cli(c_file_path)
                            # Copy the report from cantata WS to our WS folder
                            cantata_dir = os.path.dirname(c_file_path)
                            report_src = os.path.join(cantata_dir, 'Cantata', 'results', 'test_report.html')

                            report_dest = os.path.join(subfolder_path, file_name[:-2] +'test_report.html')

                            # Copy the report from cantata WS to our WS folder
                            shutil.copyfile(report_src, report_dest)
        else:
            # Directly check the files in the single folder
            for file_name in os.listdir(folder_path):
                if file_name.endswith('.c'):
                    file_path = os.path.join(folder_path, file_name)
                    # Read the .c file and write it to the destination file
                    with open(c_file_path, 'w') as dest_file:
                        with open(file_path, 'r') as src_file:
                            content = src_file.read()
                            dest_file.write(f"// From file: {file_name}\n")
                            dest_file.write(content + "\n\n")

                    execute_test_cantata_cli(c_file_path)
                        
                    # Copy the report from cantata WS to our WS folder
                    cantata_dir = os.path.dirname(c_file_path)
                    report_src = os.path.join(cantata_dir, 'Cantata', 'results', 'test_report.html')

                    report_dest = os.path.join(folder_path, file_name[:-2] +'test_report.html')

                    # Copy the report from cantata WS to our WS folder
                    shutil.copyfile(report_src, report_dest)

                            ####Move below code to outside for loop####

                            # with open(report_dest, "r", encoding="utf-8") as file:
                            #     soup = BeautifulSoup(file, 'html.parser')

                            # # Extract all rows from tables
                            # rows = soup.find_all('tr')

                            # # Target keys to extract
                            # keys_to_find = {
                            #     "Total number of test cases": None,
                            #     "Test cases passed": None,
                            #     "Test cases failed": None
                            # }

                            # # Loop through rows and look for the desired labels
                            # for row in rows:
                            #     cols = row.find_all(['td', 'th'])
                            #     if len(cols) >= 2:
                            #         label = cols[0].get_text(strip=True)
                            #         value = cols[1].get_text(strip=True)
                            #         if label in keys_to_find and keys_to_find[label] is None:
                            #             keys_to_find[label] = value

                            #     if all(value is not None for value in keys_to_find.values()):
                            #         break

                            # if int(keys_to_find["Test cases failed"]) !=0:
                            #     app.killedmutant.insert(0, "1")
                            #     app.livemutant.insert(0, "0")
                            # else:
                            #     app.killedmutant.insert(0, "0")
                            #     app.livemutant.insert(0, "1")
def execute_test_cantata_cli(c_file_path):
    def run_cmd_in_window():
    # Define the test directory using a raw string
        cantata_dir = os.path.dirname(c_file_path)
        test_dir = os.path.join(cantata_dir, 'Cantata', 'tests')
        test_dir = os.path.normpath(test_dir)
        # test_dir = r"C:\Work\MyDocs\Hackathon\Repo\Net_MonitoringClasses_UT\Net_MonitoringClasses\Cantata\tests"

        # Combine all commands into a single string for sequential execution
        full_command = (
            f"cd {test_dir} && "
            "texec -useEnv:ae.be aeee_pro/2017.1.2 && "
            "make clean && "
            "make all EXECUTE=1 OUTPUT_TO_CONSOLE=1 && "
            r"set WORKSPACE_PATH=%APPDATA%/workspace/BBM/%UBK_PRODUCT%/%UBK_PRODUCT_VERSION%/workspace && "
            f"set PROJECT_PATH={test_dir} && "
            r"aeee_pro -application com.ipl.products.eclipse.cantpp.cdt.TestReportGenerator -data %WORKSPACE_PATH% %PROJECT_PATH% HTML_DETAILED_REPORT"
        )

        # Create a command list with /k to keep the window open
        cmd_list = ['cmd.exe', '/k', full_command]

        # Execute combined commands in a new Command Prompt window
        subprocess.Popen(cmd_list, creationflags=subprocess.CREATE_NEW_CONSOLE)

    run_cmd_in_window()

    
 
    # Generate Report
    # run_cmd('set WORKSPACE_PATH=%APPDATA%/workspace/BBM/%UBK_PRODUCT%/%UBK_PRODUCT_VERSION%/workspace')
 
    # run_cmd('aeee_pro -application com.ipl.products.eclipse.cantpp.cdt.TestReportGenerator -data %WORKSPACE_PATH% %PROJECT_PATH% HTML_DETAILED_REPORT')

def open_log(app):
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

def extract_function_code(c_file_path, function_name):
    # Regular expression to match function definitions, capturing braces
    function_regex = re.compile(
        rf'^\s*[a-zA-Z_]\w*\s+{function_name}\s*\([^)]*\)\s*' + r'{[^{}]*({[^{}]*}[^{}]*)*}', re.MULTILINE)

    with open(c_file_path, 'r') as file:
        c_code = file.read()
    
    # Find the function by name
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
            popup.destroy()

    listbox.bind("<Double-1>", on_select)
