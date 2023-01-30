# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above
# copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

import os

import eu4_path_finder

config_file = open("config.cfg",'r')
lines = config_file.readlines()
config_file.close()

def get_config_data(line):
    return line.strip().split("=")[1].replace(' ','')

# Paths
EU4_FOLDER = eu4_path_finder.EU4_FOLDER
EU4_MODS = eu4_path_finder.EU4_MODS
PATH_TO_COUNTRIES_FILE = eu4_path_finder.PATH_TO_COUNTRIES_FILE
PATH_TO_BACKUP_COUNTRIES_FOLDER = eu4_path_finder.PATH_TO_BACKUP_COUNTRIES_FOLDER # Just in case we run into an issue in
# the future where a tag/country combo isn't present in 00_countries.txt, this is another place to check for (partial)
# names (it's the flags folder).
PATH_TO_FLAGS_FOLDER = eu4_path_finder.PATH_TO_FLAGS_FOLDER
PATH_TO_BACKUP_FLAG = eu4_path_finder.PATH_TO_BACKUP_FLAG
EU4_SAVE_DIR = eu4_path_finder.EU4_SAVE_DIR

MAP_TERRAIN_PATH = os.path.join(os.curdir, "graphics/mapterrain.png")
MAP_BORDERS_PATH = os.path.join(os.curdir, "graphics/mapprovinces.png")
MAP_RIVERS_PATH = os.path.join(os.curdir, "graphics/maprivers.png")
MIDPOINTS_PATH = os.path.join(os.curdir, "midpointlist.csv")

INFANTRY_GRAPHIC = os.path.join(os.curdir, "graphics/infantry_icon.png")
CAVALRY_GRAPHIC = os.path.join(os.curdir, "graphics/cavalry_icon.png")
ARTILLERY_GRAPHIC = os.path.join(os.curdir, "graphics/artillery_icon.png")
TRA_GRAPHIC = os.path.join(os.curdir, "graphics/transport_icon.png")
GAL_GRAPHIC = os.path.join(os.curdir, "graphics/galley_icon.png")
LS_GRAPHIC = os.path.join(os.curdir, "graphics/light_ship_icon.png")
HS_GRAPHIC = os.path.join(os.curdir, "graphics/big_ship_icon.png")

# Colors
C_WHITE = (255, 255, 255)
C_TRANS_WHITE = (255, 255, 0, 56)
C_ORANGE = (255, 128, 0, 200)
C_TRANS_ORANGE = (255, 128, 0, 60)
C_LGRAY = (160, 160, 160)
C_BLACK = (0, 0, 0)
C_GOLD = (255, 205, 36)
C_RED = (255, 48, 48)
# C_INTERFACE = (40,10,10)
C_INTERFACE = (10, 25, 64)
# C_INTERFACE = (36,52,72)

# Casualty vector info
CASUALTY_VECTOR_LENGTH = 21  # Length (number of values) of the casualty (loss) vector in the savefile
ATTRITION_OFFSET = 1  # Amount the attrition casualty count is offset from the start of the casualty type group (triplet)
GROUP_SIZE = 3  # Number of values corresponding to each type of unit

# Casualty vector locations
INF_START = 0
INF_END = 3
CAV_START = INF_END
CAV_END = 6
ART_START = CAV_END
ART_END = 9
HS_START = ART_END
HS_END = 12
LS_START = HS_END
LS_END = 15
GAL_START = LS_END
GAL_END = 18
TRA_START = GAL_END
TRA_END = 21

# Measurements
PAD_DIST = 10  # Pixels
FLAG_HEIGHT = 128  # Pixels
FLAG_WIDTH = 128  # Pixels
MAX_UNIT_GRAPHIC_SIZE = 43  # Pixels. Both dimensions are 43.
SMALL_UNIT_GRAPHIC_SIZE = int(MAX_UNIT_GRAPHIC_SIZE * 0.7)

try:
    START_WIDTH = int(get_config_data(lines[0]))
    START_HEIGHT = int(get_config_data(lines[1]))
except:
    START_WIDTH = 1000
    START_HEIGHT = 800
NAV_BUTTON_HEIGHT = 50  # Pixels
NAV_BUTTON_BORDER_WIDTH = 4  # Thickness, in pixels
SMALL_BORDER_WIDTH = int(NAV_BUTTON_BORDER_WIDTH / 4)
BATTLE_ENTRY_HEIGHT = 40  # Pixels
TIMELINE_WIDTH = 10
MINOR_TIME_LINE_WIDTH = 5
TIMELINE_POS = 5  # Number of positions above and below the timeline for text
MIN_TIMELINE_HEIGHT = NAV_BUTTON_HEIGHT  # Height of the lowest timeline bar
TIMELINE_LENGTH_MULTIPLIER = 2.25

BATTLE_CENTER_SIZE = 2 # Pixels radius
DATE_COLOR_SIZE = 7 # Pixels radius
BATTLE_CIRCLE_SCALING_FACTOR = 0.075
SEA_BATTLE_SCALING_FACTOR = 300  # Applied on top of the above number

SCROLL_SIZE = 1
TIMELINE_SCROLL_SIZE = 64 # Pixels here

MAP_OUTPUT_FORMAT = get_config_data(lines[3])