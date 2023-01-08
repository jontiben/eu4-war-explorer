# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above
# copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

import tkinter as tk
from tkinter import filedialog
import os
import platform

import debug_functions

operating_system = platform.system()

def find_eu4_folder():
    debug_functions.debug_out("Prompting user to select EU4 directory...")
    root = tk.Tk()
    root.withdraw()
    folder_name = filedialog.askdirectory(initialdir=os.getcwd(), title="Select your Europa Universalis IV directory")
    root.destroy()
    return folder_name


def find_eu4_mods():
    debug_functions.debug_out("Prompting user to select EU4 mods directory...")
    root = tk.Tk()
    root.withdraw()
    folder_name = filedialog.askdirectory(initialdir=os.getcwd(), title="Select your Europa Universalis IV mods "
                                                                        "directory in your Paradox Interactive folder")
    root.destroy()
    return folder_name


if operating_system == "Linux":
    EU4_FOLDER = os.path.expanduser('~') + "/.steam/steam/steamapps/common/Europa Universalis IV"
elif operating_system == "Darwin":  # OSX
    EU4_FOLDER = os.path.expanduser('~') + "/Library/Application Support/Steam/SteamApps/common/Europa Universalis IV"
else:  # Windows
    EU4_FOLDER = "C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis IV"
if not os.path.isdir(EU4_FOLDER):
    debug_functions.debug_out("EU4 directory not found automatically")
    EU4_FOLDER = ""
    while EU4_FOLDER.split('/')[-1] != "Europa Universalis IV":
        EU4_FOLDER = find_eu4_folder()
else:
    debug_functions.debug_out("EU4 directory found automatically")
PATH_TO_COUNTRIES_FOLDER = EU4_FOLDER + "/history/countries"
PATH_TO_FLAGS_FOLDER = EU4_FOLDER + "/gfx/flags"
PATH_TO_BACKUP_FLAG = PATH_TO_FLAGS_FOLDER + "/colonial_patriot_rebels.tga"

if operating_system == "Linux":
    EU4_SAVE_DIR = os.path.expanduser('~') + "/Documents/Paradox Interactive/Europa Universalis IV/save games"
    EU4_MODS = os.path.expanduser('~') + "/Documents/Paradox Interactive/Europa Universalis IV/mod"
else:  # I haven't tested this but it *should* work for OSX as well
    EU4_SAVE_DIR = os.path.expanduser('~') + "/Documents/Paradox Interactive/Europa Universalis IV/save games"
    EU4_MODS = os.path.expanduser('~') + "/Documents/Paradox Interactive/Europa Universalis IV/mod"
if not os.path.isdir(EU4_SAVE_DIR):
    EU4_SAVE_DIR = os.path.expanduser('~')
if not os.path.isdir(EU4_MODS):
    EU4_MODS = find_eu4_mods()
