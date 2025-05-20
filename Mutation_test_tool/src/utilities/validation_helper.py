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

import re
import tkinter as tk
from pathlib import Path

from src.utilities.messagebox_helper import SimpleErrorMessage
from src.utilities.messagebox_helper import SimpleInfoMessage
from src.utilities.messagebox_helper import SimpleWarnMessage

def validate_port(app, widget):

    port = widget.get()

    # Check if port is a number and in the range of 1024 to 49151
    try:
        if re.search(r'[^0-9]', port):
            SimpleErrorMessage(
                app.window,
                message=f"{widget.data}:\n\n The port number must be an integer.\n\n Please enter a valid port number.",
                title="Port Error!",
            )
            return 2
        else:
            port = int(port)
            if port < 1024 or port > 49151:
                SimpleWarnMessage(
                    app.window,
                    message=f"{widget.data}:\n\n Its recommended to use a port number between 1024 and 49151",
                    title="Port Warning!",
                )
                return 1
    except ValueError:
        SimpleErrorMessage(
            app.window,
            message=f"{widget.data}:\n\n Port number must be an integer.\n\n Please enter a valid port number.",
            title="Port Error!",
        )
        return 2

    app.window.focus_set()
    return 0

def validate_str(app, widget):

    str_content = widget.get()

    if str_content:
        if not re.match(r"^[a-zA-Z0-9_]*$", str_content):
            # Show a warning message if name contains invalid characters
            SimpleWarnMessage(
                app.window,
                message=f"{widget.data}:\n\n String Entry contains invalid characters.\n\n Please use only letters, numbers, and underscores.",
                title="String Warning!",
            )
            return 1
    else:
        # Show a warning message if name is empty
        SimpleWarnMessage(
            app.window,
            message=f"{widget.data}:\n\n String Entry cannot be empty.\n\n Please enter a valid string.",
            title="String Warning!",
        )
        return 1

    app.window.focus_set()
    return 0

def validate_date(app, widget):
    # Validate Date string is not empty and follow the format [DD/MM/YYYY]
    datestr = widget.get()

    # Check if datestr is not empty
    if not datestr:
        SimpleWarnMessage(
            app.window,
            message="Date cannot be empty. Please enter a valid date [DD/MM/YYYY].",
            title="Date Warning!",
        )
        return 1
    # Validate format [DD/MM/YYYY]
    if not re.match(r'\d{2}/\d{2}/\d{4}', datestr):
        SimpleWarnMessage(
            app.window,
            message="Date does not follow the format DD/MM/YYYY.",
            title="Date Warning!",
        )
        return 1

    app.window.focus_set()
    return 0

def validate_float(app, widget):

    number = widget.get()

    try:
        if re.search(r'[^0-9.]', number):
            SimpleErrorMessage(
                app.window,
                message='The Number must be an float.\n\n Please enter a valid float number with a "." as seperator',
                title="Float Value Error!",
            )
            return 2

        number = float(number)

    except ValueError:
        SimpleErrorMessage(
            app.window,
            message='The Number must be an float.\n\n Please enter a valid float number with a "." as seperator',
            title="Float Value Error!",
        )
        return 2

    app.window.focus_set()
    return 0

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

def validate_key(app, widget):

    number = widget.get()

    # Check if the input starts with '{' and ends with '}'
    if not (number.startswith('[') and number.endswith(']')):
        SimpleErrorMessage(
                app.window,
                message='Key should be with square brackets',
                title="Car Key Error!",
            )
        raise ValueError(f"Problem to get entry for Car Key! Please specify a proper value")
    
    # Remove the curly braces and split the entries
    entries = number[1:-1].split(',')

    # Check if there are exactly 16 entries
    if len(entries) != 32:
        SimpleErrorMessage(
                app.window,
                message='Car Key must be exactly 32 bytes',
                title="Car Key Error!",
            )
        raise ValueError(f"Problem to get entry for Car Key! Please specify a proper value")

    # Define a regex pattern to match the required format
    hex_pattern = re.compile(r'^\s*0x[0-9A-Fa-f]{2}\s*$')

    # Validate each entry
    for entry in entries:
        if not hex_pattern.match(entry):
            SimpleErrorMessage(
                app.window,
                message='Invalid entry. Each key entry must be in the format 0xNN, where NN are hex digits',
                title="Car Key Error!",
            )
            raise ValueError(f"Problem to get entry for Car Key! Please specify a proper value")
            

    app.window.focus_set()
    return 0

def validate_id(app, widget, show_display=True):

    frame_id = widget.get()

    # ID can be a number as normal integer or a hex number
    try:
        if re.search(r'[^0-9A-Fa-fxX]', frame_id):
            SimpleErrorMessage(
                app.window,
                message="The ID must be an integer or a hex number. Please enter a valid ID.",
                title="ID Value Error!",
            )
            return 2

    except ValueError:
        SimpleErrorMessage(
            app.window,
            message="The ID must be an integer or a hex number. Please enter a valid ID.",
            title="ID Value Error!",
        )
        return 2

    app.window.focus_set()
    if show_display:
        frame_id = widget.get()

        if frame_id != "":
            if "0x" in frame_id or "0X" in frame_id:
                frame_id = frame_id.replace("0X", "")
                frame_id = frame_id.replace("0x", "")
                frame_id = int(frame_id, 16)
            else:
                frame_id = int(frame_id)

            if widget.data == "dec":
                widget.delete(0, tk.END)
                widget.insert(0, str(frame_id))
            elif widget.data == "hex":
                widget.delete(0, tk.END)
                widget.insert(0, str(hex(frame_id)))
        else:
            SimpleErrorMessage(
                app.window,
                message="The ID can not be empty. Please enter a valid ID.",
                title="ID Value Error!",
            )
            return 2
    return 0

def validate_folder(app, widget, present=True):

    path = widget.get()

    if not path:
        SimpleErrorMessage(
            app.window,
            message=f"{widget.data}:\n\n The directory cannot be empty.\n\n Please enter a valid directory.",
            title="Directory Error!",
        )
        return 2

    try:
        if (re.search(r'[^a-zA-Z0-9_.:/\\]', path)):
            SimpleErrorMessage(
                app.window,
                message=f"{widget.data}:\n\n The directory contains invalid characters.\n\n Please enter a valid directory.",
                title="Directory Error!",
            )
            return 2

        # Check if path contains \
        if "\\" in path:
            SimpleWarnMessage(
                app.window,
                message=f"{widget.data}:\n\n The directory contains backslashes.\n\n Please use forward slashes in the path.",
                title="Directory Warning!",
            )
            return 1

        if not Path(path).exists():
            if present:
                SimpleErrorMessage(
                    app.window,
                    message=f"{widget.data}:\n\n The directory does not exist.\n\n Please enter a valid directory.",
                    title="Directory Error!",
                )
                return 2
            else:
                SimpleInfoMessage(
                    app.window,
                    message=f"{widget.data}:\n\n The directory is not present on this system.\n\n Please make sure the directory exists on target system for execution.",
                    title="Directory Info!",
                )
    except ValueError:
        SimpleErrorMessage(
            app.window,
            message=f"{widget.data}:\n\n The directory does not exist.\n\n Please enter a valid directory.",
            title="Directory Error!",
        )
        return 2

    app.window.focus_set()
    return 0
