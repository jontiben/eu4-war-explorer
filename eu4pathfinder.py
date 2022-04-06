#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

import tkinter as tk
from tkinter import filedialog
import os
import debugfunctions

def find_eu4_folder():
	debugfunctions.debug_out("Prompting user to select EU4 directory...")
	root = tk.Tk()
	root.withdraw()
	folder_name = filedialog.askdirectory(initialdir = os.getcwd(),title='Select your Europa Universalis IV directory')
	root.destroy()
	return folder_name

debugfunctions.debug_out("Detecting EU4 directory in [C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis IV]...")
EU4_FOLDER = "C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis IV"
if not os.path.isdir(EU4_FOLDER):
	debugfunctions.debug_out("EU4 directory not found")
	EU4_FOLDER = ""
	while EU4_FOLDER.split('/')[-1] != "Europa Universalis IV":
		EU4_FOLDER = find_eu4_folder()
else:
	debugfunctions.debug_out("EU4 directory found automatically	")
PATH_TO_COUNTRIES_FOLDER = EU4_FOLDER+"/history/countries"
PATH_TO_FLAGS_FOLDER = EU4_FOLDER+"/gfx/flags"
PATH_TO_BACKUP_FLAG = PATH_TO_FLAGS_FOLDER+"/colonial_patriot_rebels.tga"

EU4_SAVE_DIR = os.path.expanduser("~")+"/Documents/Paradox Interactive/Europa Universalis IV/save games"
if not os.path.isdir(EU4_SAVE_DIR):
	EU4_SAVE_DIR = os.path.expanduser("~")
