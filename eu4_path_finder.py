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
    debug_functions.hold_until_start("Prompting user to select EU4 directory...")
    root = tk.Tk()
    root.withdraw()
    folder_name = filedialog.askdirectory(initialdir=os.getcwd(), title="Select your Europa Universalis IV folder ("
                                                                        "NOT in Paradox Interactive/-)")
    root.destroy()
    write_to_file = True
    with open("config.cfg", 'r') as config_file:
        for line in config_file.readlines():
            if get_config_tag(line) == "mods folder":
                write_to_file = False
    if write_to_file:
        debug_functions.hold_until_start("Saving specified EU4 directory to config.cfg...")
        out_config = open("config.cfg", 'a')
        out_config.write(f"\neu4 folder={folder_name}\n")
        out_config.close()
    return folder_name


def find_eu4_mods():
    debug_functions.hold_until_start("Prompting user to select EU4 mods directory...")
    root = tk.Tk()
    root.withdraw()
    folder_name = filedialog.askdirectory(initialdir=os.getcwd(), title="Select your Europa Universalis IV mods "
                                                                        "directory in your Paradox Interactive folder")
    root.destroy()
    write_to_file = True
    with open("config.cfg", 'r') as config_file:
        for line in config_file.readlines():
            if get_config_tag(line) == "mods folder":
                write_to_file = False
    if write_to_file:
        debug_functions.hold_until_start("Saving specified mods directory to config.cfg...")
        out_config = open("config.cfg", 'a')
        out_config.write(f"\nmods folder={folder_name}")
        out_config.close()
    return folder_name


config_file = open("config.cfg", 'r')
lines = config_file.readlines()
config_file.close()


# Checking the config file
def get_config_data(line):
    try:
        return line.strip().split("=")[1].strip().split(";")[0].strip()
    except: # it's okay, this mostly just handles blank lines
        return None


def get_config_tag(line):
    try:
        return line.strip().split("=")[0]
    except:
        return None


EU4_FOLDER, EU4_MODS = None, None
for line in lines:
    if "eu4 folder" in get_config_tag(line):
        if os.path.isdir(get_config_data(line)):
            EU4_FOLDER = get_config_data(line)
    elif "mods folder" in get_config_tag(line):
        if os.path.isdir(get_config_data(line)):
            EU4_MODS = get_config_data(line)

if EU4_FOLDER is None:
    if operating_system == "Linux":
        EU4_FOLDER = os.path.expanduser('~') + "/.steam/steam/steamapps/common/Europa Universalis IV"
    elif operating_system == "Darwin":  # OSX
        EU4_FOLDER = os.path.expanduser('~') + "/Library/Application Support/Steam/SteamApps/common/Europa Universalis IV"
    else:  # Windows
        EU4_FOLDER = "C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis IV"
        if not os.path.isdir(EU4_FOLDER):
            "D:/Program Files (x86)/Steam/steamapps/common/Europa Universalis IV"
        if not os.path.isdir(EU4_FOLDER):
            "E:/Program Files (x86)/Steam/steamapps/common/Europa Universalis IV"

    if not os.path.isdir(EU4_FOLDER):
        debug_functions.hold_until_start("EU4 directory not found automatically")
        EU4_FOLDER = ""
        while EU4_FOLDER.split('/')[-1] != "Europa Universalis IV":
            EU4_FOLDER = find_eu4_folder()
    else:
        debug_functions.hold_until_start("EU4 directory found automatically")
else:
    debug_functions.hold_until_start(f"EU4 folder specified in config as {EU4_FOLDER}")
PATH_TO_COUNTRIES_FILE = EU4_FOLDER + "/common/country_tags/00_countries.txt"
PATH_TO_BACKUP_COUNTRIES_FOLDER = EU4_FOLDER + "/history/countries"
PATH_TO_FLAGS_FOLDER = EU4_FOLDER + "/gfx/flags"
PATH_TO_BACKUP_FLAG = PATH_TO_FLAGS_FOLDER + "/colonial_patriot_rebels.tga"
PATH_TO_CONDOTTIERI_FLAG = PATH_TO_FLAGS_FOLDER + "/ronin_rebels.tga"
if not os.path.isfile(PATH_TO_BACKUP_FLAG): # Just in case
    PATH_TO_BACKUP_FLAG = PATH_TO_FLAGS_FOLDER + "/heretic_rebels.tga"
if not os.path.isfile(PATH_TO_CONDOTTIERI_FLAG):
    PATH_TO_CONDOTTIERI_FLAG = PATH_TO_BACKUP_FLAG

if EU4_MODS is None:
    if operating_system == "Linux":
        EU4_MODS = os.path.expanduser('~') + "/Documents/Paradox Interactive/Europa Universalis IV/mod"
    else:  # I haven't tested this but it *should* work for OSX as well
        EU4_MODS = os.path.expanduser('~') + "/Documents/Paradox Interactive/Europa Universalis IV/mod"
        if not os.path.isdir(EU4_MODS) and operating_system == "Windows": # ^^
            if not os.path.isdir(EU4_MODS.replace("/Europa Universalis IV/mod", "/Europa Universalis IV")): # just missing mod folder
                EU4_MODS = os.path.expanduser('~') + "/OneDrive/Documents/Paradox Interactive/Europa Universalis IV/mod"
            else:
                EU4_MODS = os.path.expanduser('~') + "/OneDrive/Documents/Paradox Interactive/Europa Universalis IV"
else:
    debug_functions.hold_until_start(f"Mods folder specified in config as {EU4_MODS}")

if operating_system == "Linux":
    EU4_SAVE_DIR = os.path.expanduser('~') + "/Documents/Paradox Interactive/Europa Universalis IV/save games"
else:  # I haven't tested this but it *should* work for OSX as well
    EU4_SAVE_DIR = os.path.expanduser('~') + "/Documents/Paradox Interactive/Europa Universalis IV/save games"
    if not os.path.isdir(EU4_SAVE_DIR) and operating_system == "Windows":  # Some people's installs are cursed this way
        EU4_SAVE_DIR = os.path.expanduser(
            '~') + "/OneDrive/Documents/Paradox Interactive/Europa Universalis IV/save games"

if not os.path.isdir(EU4_SAVE_DIR): # Final fallback
    EU4_SAVE_DIR = os.path.expanduser('~')
if not os.path.isdir(EU4_MODS):
    EU4_MODS = find_eu4_mods()
