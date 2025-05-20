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

from CTkMessagebox import CTkMessagebox

class BaseMessageBox(CTkMessagebox):
    """
    A base class for message boxes with common functionality
    """
    def __init__(self, master, message, title, icon):
        """
        Initialize the BaseMessageBox with a message, title, and icon
        """
        if master.data == "blocked":
            # If the master window is blocked, return because another message is active
            return

        # Preprocess the message to remove whitespace after newline characters
        formatted_message = re.sub(r'\n\s+', '\n', message)

        # # Draw an empty frame over the complete window (master) as a shadow
        # self.shadow_frame = tk.Frame(master, bg=master.cget("bg"), bd=0)
        # self.shadow_frame.place(relwidth=1.0, relheight=1.0)  # Cover the entire window

        # Optionally, you can set the opacity of the shadow frame if your system supports it
        master.attributes('-alpha', 0.92)
        master.data = "blocked"

        super().__init__(
            master=master,
            width=520,
            height=280,
            justify="center",
            title=title,
            message=formatted_message,
            icon=icon,
            option_1="Ok",
            border_width=2,
            bg_color="gray85",
            button_color="gray90",
            corner_radius=8,
            border_color="gray40",
            fade_in_duration=0.4,
            icon_size=(50, 50),
            option_focus=1,
            topmost=True,
        )
        self.title_label._font.configure(size=14)
        master.focus_set()

        # Bind the destroy_shadow_frame method to the button click event
        self.button_1.configure(command=lambda: self.destroy_shadow_frame(master))
        self.button_close.configure(command=lambda: self.destroy_shadow_frame(master))

    def destroy_shadow_frame(self, master):
        """Destroy the shadow frame and close the message box"""
        # self.shadow_frame.destroy()
        self.destroy()  # Close the message box
        master.attributes('-alpha', 1)
        master.data = "unblocked"
        master.focus_set()

class SimpleInfoMessage(BaseMessageBox):
    """
    A simple info message box class
    """
    def __init__(self, master, message, title="Info!"):
        """
        Initialize the SimpleWarnMessage with a warning message
        """
        super().__init__(master, message, title, icon="info")

class SimpleWarnMessage(BaseMessageBox):
    """
    A simple warning message box class
    """
    def __init__(self, master, message, title="Warning!"):
        """
        Initialize the SimpleWarnMessage with a warning message
        """
        super().__init__(master, message, title, icon="warning")

class SimpleErrorMessage(BaseMessageBox):
    """
    A simple error message box class
    """
    def __init__(self, master, message, title="Error!"):
        """
        Initialize the SimpleErrorMessage with an error message
        """
        super().__init__(master, message, title, icon="cancel")

class SimpleSuccessMessage(BaseMessageBox):
    """
    A simple success message box class
    """
    def __init__(self, master, message, title="Success!"):
        """
        Initialize the SimpleSuccessMessage with a success message
        """
        super().__init__(master, message, title, icon="check")
