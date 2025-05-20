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

import customtkinter as ctk
from CTkToolTip import CTkToolTip

from src.utilities.validation_helper import validate_folder
from src.utilities.validation_helper import validate_port
from src.utilities.validation_helper import validate_str

class ToolTip(CTkToolTip):
    """
    A custom widget tooltip class that inherits from CTkToolTip
    """
    def __init__(self, master, message):
        # Preprocess the message to remove whitespace after newline characters
        formatted_message = re.sub(r'\n\s+', '\n', message)

        if master._name == '!widgetlabel':
            delay=0.6
        else:
            delay=1.5

        super().__init__(
            widget=master,
            message=formatted_message,
            corner_radius=1,
            alpha=0.95,
            delay=delay,
            bg_color="#fceecf",
        )
class WidgetLabel(ctk.CTkLabel):
    """
    A custom widget label class that inherits from ctk.CTkLabel
    """
    def __init__(self, master, text, anchor=tk.W, row=0, column=0, columnspan=1, padx=5, pady=5, sticky=tk.EW, tooltip=None, **kwargs):
        """
        Initialize the WidgetLabel with the provided parameters
        """
        super().__init__(master, text=text, anchor=anchor, **kwargs)
        self.grid(columnspan=columnspan,row=row, column=column,padx=padx, pady=pady, sticky=sticky)

        if tooltip is not None:
            ToolTip(self, tooltip)

class BaseEntry(ctk.CTkEntry):
    """
    A base class for custom entry widgets that inherits from ctk.CTkEntry
    """
    def __init__(self, app, master, placeholder="", description="", row=0, column=0, columnspan=1, padx=5, pady=5, sticky=tk.EW, tooltip=None, width=None, validatecommand=None, **kwargs):
        """
        Initialize the BaseEntry with the provided parameters
        """
        if width is not None:
            super().__init__(master, placeholder_text=placeholder, width=width, **kwargs)
        else:
            super().__init__(master, placeholder_text=placeholder, **kwargs)

        self.data = description
        self.bind("<Return>", lambda event: app.window.focus_set())
        if validatecommand is not None:
            self.configure(validate="focusout", validatecommand=validatecommand)
        self.grid(columnspan=columnspan, row=row, column=column, padx=padx, pady=pady, sticky=sticky)

        if tooltip is not None:
            ToolTip(self, tooltip)

class StringEntry(BaseEntry):
    """
    A custom string entry class that inherits from BaseEntry
    """
    def __init__(self, app, master, placeholder="", description="", row=0, column=0, columnspan=1, padx=5, pady=5, sticky=tk.EW, tooltip=None, width=None, **kwargs):
        """
        Initialize the StringEntry with the provided parameters
        """
        super().__init__(app, master, placeholder, description, row, column, columnspan, padx, pady, sticky, tooltip, width, validatecommand=lambda: validate_str(app, self), **kwargs)

class PortEntry(BaseEntry):
    """
    A custom port entry class that inherits from BaseEntry
    """
    def __init__(self, app, master, placeholder="", description="", row=0, column=0, columnspan=1, padx=5, pady=5, sticky=tk.EW, tooltip=None, width=None, **kwargs):
        """
        Initialize the PortEntry with the provided parameters
        """
        super().__init__(app, master, placeholder, description, row, column, columnspan, padx, pady, sticky, tooltip, width, validatecommand=lambda: validate_port(app, self), **kwargs)

class FolderEntry(BaseEntry):
    """
    A custom folder entry class that inherits from BaseEntry
    """
    def __init__(self, app, master, placeholder="", description="", row=0, column=0, columnspan=1, padx=5, pady=5, sticky=tk.EW, tooltip=None, width=None, folder_present=True, **kwargs):
        """
        Initialize the FolderEntry with the provided parameters
        """
        super().__init__(app, master, placeholder, description, row, column, columnspan, padx, pady, sticky, tooltip, width, validatecommand=lambda: validate_folder(app, self, folder_present), **kwargs)
