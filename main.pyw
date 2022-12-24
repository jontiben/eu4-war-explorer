# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above
# copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

import pygame
import tkinter as tk
from tkinter import filedialog
import traceback, os

import midpoint_calculator
import save_file_reader
import war_info_interface
import war_list_interface
import defines
import debug_functions

### VERSION
VERSION = "1.0"

do_quit = False
mode = "list"
war_list = []
has_updated_for_resize = False
curr_filename = None


def clear_debug_file():
    # Blanks debug.txt
    debug_file = open("debug.txt", 'w')
    debug_file.write("")
    debug_file.close()


clear_debug_file()

pygame.init()

screen_info = pygame.display.Info()
start_width = int(screen_info.current_w * 0.7)
start_height = int(screen_info.current_h * 0.75)
window = pygame.display.set_mode((start_width, start_height), pygame.RESIZABLE)
caption_root = "EU4 War Explorer - " + VERSION
pygame.display.set_caption(caption_root)
pygame.display.set_icon(pygame.image.load(defines.INFANTRY_GRAPHIC))

# Fonts
# Pygame has to be initialized with the fonts so these can't be put in the defines.py module
FONT = pygame.font.Font("fonts/Dosis-SemiBold.ttf", 32)
SMALL_FONT = pygame.font.Font("fonts/Dosis-SemiBold.ttf", 24)
LIGHT_FONT = pygame.font.Font("fonts/Dosis-Light.ttf", 32)
STATS_FONT = pygame.font.Font("fonts/UbuntuMono-Regular.ttf", 24)


def disp_resize(screen_size):
    # Resizes the window
    global window
    window = pygame.display.set_mode(screen_size, pygame.RESIZABLE)
    pygame.display.update()


def debug_mode_out():
    # Outputs the current mode to the debug.txt file
    debug_functions.debug_out(mode, event_type="mode")


def open_file():
    global do_quit
    # Opens a file using a tkinter dialog
    debug_functions.debug_out("Waiting for the user to select a file...")
    root = tk.Tk()
    root.withdraw()
    try:
        file_name = filedialog.askopenfilename(initialdir=defines.EU4_SAVE_DIR, title='Select an EU4 Savefile',
                                               filetypes=[('eu4 save files', '*.eu4')])
    except:
        debug_functions.debug_out(
            f"Exception [{traceback.format_exc()}] while prompting the user to select a file, user likely closed the "
            f"file dialog without making a selection.")
        do_quit = True
        return None
    root.destroy()
    return file_name

def init():
    global do_quit
    try:
        # Loads a new map and runs save_file_reader.py
        global has_updated_for_resize
        global curr_filename, mode, war_list, present_date
        global MAP_TERRAIN, MAP_RIVERS, MAP_BORDERS, MIDPOINTS_PATH
        try_counts = 0
        while curr_filename is None:
            # This is necessary because sometimes tkinter exits with a "catastrophic error." This is
            # usually tied to multithreading, which I'm not using, so in lieu of an actual solution
            # I'm just gonna have it try to open the prompt 20 times until it succeeds.
            if try_counts > 20:
                debug_functions.debug_out("Tkinter failed to open dialog too many times. Exiting.")
                return
            try:
                curr_filename = open_file()
            except:
                try_counts += 1
                debug_functions.debug_out(
                    "Tkinter failed to open dialog, likely due to Tkinter giving a catastrophic error. Trying again.",
                    event_type="ERROR")
        if not do_quit:
            window.fill(defines.C_BLACK)
            load_text = FONT.render("Loading...", True, defines.C_WHITE)
            load_text_loc = load_text.get_rect()
            load_text_loc.center = (int(window.get_width() / 2), int(window.get_height() / 2))
            window.blit(load_text, load_text_loc)
            pygame.display.update()

            has_updated_for_resize = True

            save_file_reader_out = save_file_reader.locate_wars(curr_filename)
            if save_file_reader_out is None:
                do_quit = True
                return
            war_list = save_file_reader_out[0]
            present_date = save_file_reader_out[1]
            map_mod_location = save_file_reader_out[2]
            MAP_TERRAIN = pygame.image.load(defines.MAP_TERRAIN_PATH)
            MAP_RIVERS = pygame.image.load(defines.MAP_RIVERS_PATH)
            MAP_BORDERS = pygame.image.load(defines.MAP_BORDERS_PATH)
            MIDPOINTS_PATH = defines.MIDPOINTS_PATH
            if map_mod_location is not None: ### MAKE SURE RANDOM GRAPHICS MODS DON'T OVERWRITE THIS
                MAP_TERRAIN = pygame.image.load(map_mod_location+"/terrain.bmp")
                try:
                    MAP_RIVERS = pygame.image.load(map_mod_location+"/rivers.bmp")
                    MAP_BORDERS = pygame.image.load(map_mod_location+"/provinces.bmp")
                except:
                    debug_functions.debug_out(f"Could not find a rivers or borders map for the modded map folder "
                                              f"located at {map_mod_location}", event_type="WARN")
                if os.path.isfile(map_mod_location+"/provinces.bmp") and os.path.isfile(map_mod_location+"/definition.csv"):
                    path_to_test_for = os.getcwd()+f"/mod_data/{map_mod_location.split('/')[-2]}midpointlist.csv"
                    if os.path.isfile(path_to_test_for):
                        debug_functions.debug_out(f"Found previously generated province midpoint list for mod", event_type="INFO")
                        MIDPOINTS_PATH = path_to_test_for
                    else:
                        debug_functions.debug_out(f"Modded map found, generating new province midpoints list...")
                        MIDPOINTS_PATH = midpoint_calculator.get_midpoints(map_mod_location)
                        debug_functions.debug_out(f"Province midpoints list generated at {MIDPOINTS_PATH}")

            mode = "list"

            #debug_mode_out()
            war_list_interface.list_loop(window, FONT, SMALL_FONT, war_list, None, force_update=True)
            pygame.display.update()
            pygame.display.set_caption(caption_root + " - " + curr_filename.split('/')[-1])

    except:
        debug_functions.debug_out(f"Exception [{traceback.format_exc()}] while initializing save")


def render_scene(event):
    global window, mode, has_updated_for_resize, curr_filename
    try:
        if mode == "list":  # The window/scene that's active
            list_out = war_list_interface.list_loop(window, FONT, SMALL_FONT, war_list, event,
                                                    force_update=(not has_updated_for_resize))
            if list_out is not None:
                if list_out == "open":
                    curr_filename = None
                    init()
                    return
                else:
                    mode = "info"
                    #debug_mode_out()
                    war_info_interface.init(window, FONT, SMALL_FONT, LIGHT_FONT, STATS_FONT, MAP_TERRAIN,
                                            MAP_RIVERS, MAP_BORDERS, list_out)
        elif mode == "info":
            poss_prev_window = war_info_interface.info_loop(window, FONT, SMALL_FONT, LIGHT_FONT, STATS_FONT,
                                                            MAP_TERRAIN, MAP_RIVERS, MAP_BORDERS, MIDPOINTS_PATH, event,
                                                            present_date, force_update=(not has_updated_for_resize))
            if poss_prev_window is not None:
                mode = "list"
                #debug_mode_out()
                war_list_interface.list_loop(window, FONT, SMALL_FONT, war_list, event, force_update=True)
        has_updated_for_resize = True
    except:
        debug_functions.debug_out(f"Exception [{traceback.format_exc()}] on rendering scene [{mode}]")


def main():
    global do_quit, has_updated_for_resize
    try:
        while not do_quit:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    do_quit = True
                elif event.type == pygame.VIDEORESIZE:
                    # When pygame.event.get() is called in a function, for some reason it never gets
                    # pygame.VIDEORESIZE events. That's why I'm dealing with the important things (quitting and
                    # resizing) out here. All other inputs eventually get passed to the various modules and they can
                    # figure out what to do with them.
                    disp_resize(event.size)
                    has_updated_for_resize = False
                else:
                    render_scene(event)

        debug_functions.debug_out("Exited normally")

    except:
        debug_functions.debug_out(f"Program crashed, exiting with exception [{traceback.format_exc()}]")


if __name__ == "__main__":
    debug_functions.debug_out(f"Started EU4 Savefile Explorer version {VERSION}")
    init()
    main()
