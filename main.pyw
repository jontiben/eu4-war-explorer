# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above
# copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

import pygame
import tkinter as tk
from tkinter import filedialog
import traceback, os, platform

import defines
import midpoint_calculator
import save_file_reader
import war_info_interface
import war_list_interface
import debug_functions

do_quit = False
mode = "list"
war_list = []
has_updated_for_resize = False
curr_filename = None
list_position = 0


def clear_debug_file():
    # Copies debug.txt to debug_backup.txt and blanks it
    try:
        debug_file = open("debug.txt", 'r')
        debug_backup_file = open("debug_backup.txt", 'w')
        debug_backup_file.write(debug_file.read())
        debug_backup_file.close()
        debug_file.close()
    except OSError: # No debug file yet
        pass
    debug_file = open("debug.txt", 'w')
    debug_file.write("")
    debug_file.close()


pygame.init()

screen_info = pygame.display.Info()
window = pygame.display.set_mode((int(defines.START_WIDTH), int(defines.START_HEIGHT)), pygame.RESIZABLE)
caption_root = "EU4 War Explorer - " + defines.VERSION
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
    debug_functions.new_save()
    # Opens a file using a tkinter dialog
    debug_functions.debug_out("Waiting for the user to select a file...")
    root = tk.Tk()
    root.withdraw()
    try:
        # Sometimes this breaks on my computer. I suspect it's an issue with my OS install or the TK library or
        # something equally cursed. It doesn't give an exception or traceback, just crashes with:
        # "Process finished with exit code -1073740771 (0xC000041D)." I'm not sure whether those of us who walk the
        # mortal plane as men have the spiritual pull to deal with something this deeply haunted, so I'm not going
        # to touch it for now. I haven't introduced this issue with this update because it crops up in old versions of
        # the program as well, versions where I know for a fact it used to consistently work. Miserere mei, Deus.
        file_name = filedialog.askopenfilename(parent=root, initialdir=defines.EU4_SAVE_DIR, title="Select an EU4 Savefile",
                                               filetypes=[('eu4 save files', '*.eu4')])
    except:
        debug_functions.debug_out(
            f"Exception [{traceback.format_exc()}] while prompting the user to select a file, user likely closed the "
            f"file dialog without making a selection.", event_type="ERROR")
        do_quit = True
        root.destroy()
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
            checksum = save_file_reader_out[3]
            game_version = save_file_reader_out[4]
            debug_functions.debug_out(f"Game version is {game_version}", event_type="INFO")
            debug_functions.debug_out(f"Checksum is {checksum}", event_type="INFO")
            MAP_TERRAIN = pygame.image.load(defines.MAP_TERRAIN_PATH)
            MAP_RIVERS = pygame.image.load(defines.MAP_RIVERS_PATH)
            MAP_BORDERS = pygame.image.load(defines.MAP_BORDERS_PATH)
            MIDPOINTS_PATH = defines.MIDPOINTS_PATH
            if map_mod_location is not None:
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
                        debug_functions.debug_out(f"Found previously generated province midpoint list for mod at {path_to_test_for}")
                        MIDPOINTS_PATH = path_to_test_for
                    else:
                        debug_functions.debug_out(f"Modded map found, generating new province midpoints list...")
                        MIDPOINTS_PATH = midpoint_calculator.get_midpoints(map_mod_location)
                        debug_functions.debug_out(f"Province midpoints list generated at {MIDPOINTS_PATH}")

            mode = "list"

            #debug_mode_out()
            war_list_interface.list_loop(window, FONT, SMALL_FONT, war_list, None, force_update=True, force_reset_list=True)
            pygame.display.update()
            pygame.display.set_caption(caption_root + " - " + curr_filename.split('/')[-1])

    except:
        debug_functions.debug_out(f"Exception [{traceback.format_exc()}] while initializing save", event_type="ERROR")


def render_scene(event):
    global window, mode, has_updated_for_resize, curr_filename, list_position
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
                    debug_functions.debug_out(f"Viewing war [{list_out[0].title}]")
                    list_position = list_out[1]
                    war_info_interface.init(window, FONT, SMALL_FONT, LIGHT_FONT, STATS_FONT, MAP_TERRAIN,
                                            MAP_RIVERS, MAP_BORDERS, list_out[0])
        elif mode == "info":
            poss_prev_window = war_info_interface.info_loop(window, FONT, SMALL_FONT, LIGHT_FONT, STATS_FONT,
                                                            MAP_TERRAIN, MAP_RIVERS, MAP_BORDERS, MIDPOINTS_PATH, event,
                                                            present_date, force_update=(not has_updated_for_resize))
            if poss_prev_window is not None:
                mode = "list"
                war_list_interface.list_loop(window, FONT, SMALL_FONT, war_list, event, force_update=True, force_reset_list=False, position=list_position)
        has_updated_for_resize = True
    except:
        debug_functions.debug_out(f"Exception [{traceback.format_exc()}] on rendering scene [{mode}]", event_type="ERROR")


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
        debug_functions.debug_out(f"Program crashed, exiting with exception [{traceback.format_exc()}]", event_type="ERROR")


if __name__ == "__main__":
    clear_debug_file()
    debug_functions.debug_out(f"Started EU4 Savefile Explorer version {defines.VERSION}")
    debug_functions.debug_out(f"OS is {platform.system()} {platform.release()}", event_type="INFO")
    debug_functions.output_message_backlog()
    init()
    main()
