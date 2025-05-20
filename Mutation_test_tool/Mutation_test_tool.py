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
import tkinter as tk

import customtkinter as ctk
from PIL import Image
from src.general.general_tab import setup_general_tab
from src.menu.menu import setup_menu


# Define App Paths
# ********************************************************************************
script_directory = os.path.dirname(os.path.abspath(__file__))

default_json_path = os.path.join(script_directory, "assets", "default")
docs_path = os.path.join(script_directory, "assets", "docs")

themes_path = os.path.join(script_directory, "assets", "themes", "vNP_Themes.json")
icon_path = os.path.join(script_directory, "assets", "img", "Logo.ico")
transparent_path = os.path.join(script_directory, "assets", "img", "transparent.jpg")
footer_path = os.path.join(script_directory, "assets", "img", "Digital_Banner.png")
logger_path = os.path.join(script_directory, "assets", "log", "vNP_ConfigTool.log")
utilities_path = os.path.join(script_directory, "assets", "utilities")

# Define App appearance and Styles
# ********************************************************************************
ctk.set_appearance_mode("light")
ctk.set_default_color_theme(themes_path)
ctk.deactivate_automatic_dpi_awareness()

# Define Logger
# ********************************************************************************

# Define App
# ********************************************************************************
class ConfigToolApp:
    """
    vNP Configuration Tool Class
    """
    def __init__(self):
        """
        Initialize the Tool App
        """
        # Initialize Logger
        # ********************************************************************************
        # self.logger.debug("Initializing Tool App")

        # Set App Interpaths
        # ********************************************************************************
        self.script_directory = script_directory
        self.default_json_path = default_json_path
        self.docs_path = docs_path
        self.utilities_path = utilities_path
        self.logger_path = logger_path


        self._define_app_colors()

        self._create_window()

        self._create_header()

        self._create_main_tab_view()

        self._create_footer()


    # Define App Colors
    # ********************************************************************************
    def _define_app_colors(self):
        """
        Define application colors
        """
        self.header_color = ctk.ThemeManager.theme["CTkNamedFrame"]["header_color"]
        self.header_font = ctk.ThemeManager.theme["CTkHeaderFont"]
        self.bg_color = ctk.ThemeManager.theme["CTk"]["fg_color"]

    # Create Window
    # *********************************************************************************************
    def _create_window(self):
        """
        Create the main application window
        """
        self.window = ctk.CTk()
        self.window.minsize(width=1280, height=780)
        self.window.title("Mutation Testing Tool")
        self.window.iconbitmap(icon_path)
        self.window.data = "unblocked"


    # Create Header
    # *********************************************************************************************
    def _create_header(self):
        """
        Create the application header
        """
        header = ctk.CTkLabel(
            self.window, text="Mutation Testing Tool",
            font=("@Bosch Sans Global", 24), height=35,
        )
        header.pack(fill=tk.X, side=tk.TOP)

    # Create MainTabView
    # *********************************************************************************************
    def _create_main_tab_view(self):
        """
        Create the main tab view
        """
        self.tabv_main = ctk.CTkTabview(self.window, border_width=1, anchor="nw")
        self.tabv_main.pack(fill=tk.BOTH, side=tk.TOP, expand=tk.TRUE)
        setup_general_tab(self)
        self.tabv_main.set("General".center(40))

    # Create Footer
    # *********************************************************************************************
    def _create_footer(self):
        """
        Create the application footer
        """
        footer_img = ctk.CTkImage(
            light_image=Image.open(footer_path),
            dark_image=Image.open(footer_path), size=(1280, 5),
        )
        footer = ctk.CTkLabel(self.window, image=footer_img, text="", height=10)
        footer.pack(fill=tk.X, side=tk.BOTTOM)

    # *********************************************************************************************
    # Run Application
    # *********************************************************************************************
    def run(self):
        """
        Run method for infinite main loop
        """
        self.window.mainloop()

# Main
# ********************************************************************************
if __name__ == "__main__":
    app = ConfigToolApp()

    # app.logger.debug("Application initialized.")
    app.run()
    # app.logger.debug("Application closed.")
