#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

import pygame
import os
import eu4pathfinder

# 
# Paths
EU4_FOLDER = eu4pathfinder.EU4_FOLDER
PATH_TO_COUNTRIES_FOLDER = eu4pathfinder.PATH_TO_COUNTRIES_FOLDER
PATH_TO_FLAGS_FOLDER = eu4pathfinder.PATH_TO_FLAGS_FOLDER
PATH_TO_BACKUP_FLAG = eu4pathfinder.PATH_TO_BACKUP_FLAG
EU4_SAVE_DIR = eu4pathfinder.EU4_SAVE_DIR

MAP_TERRAIN_PATH = os.path.join(os.curdir,"graphics/mapterrain.png")
MAP_BORDERS_PATH = os.path.join(os.curdir,"graphics/mapprovinces.png")
MAP_RIVERS_PATH = os.path.join(os.curdir,"graphics/maprivers.png")

INFANTRY_GRAPHIC = os.path.join(os.curdir,"graphics/infantry_icon.png")
CAVALRY_GRAPHIC = os.path.join(os.curdir,"graphics/cavalry_icon.png")
ARTILLERY_GRAPHIC = os.path.join(os.curdir,"graphics/artillery_icon.png")
TRA_GRAPHIC = os.path.join(os.curdir,"graphics/transport_icon.png")
GAL_GRAPHIC = os.path.join(os.curdir,"graphics/galley_icon.png")
LS_GRAPHIC = os.path.join(os.curdir,"graphics/light_ship_icon.png")
HS_GRAPHIC = os.path.join(os.curdir,"graphics/big_ship_icon.png")


# Colors
C_WHITE = (255,255,255)
C_TRANS_WHITE = (255,255,0,56)
C_ORANGE = (255,128,0,200)
C_TRANS_ORANGE = (255,128,0,84)
C_LGRAY = (160,160,160)
C_BLACK = (0,0,0)
C_GOLD = (255,205,36)
C_RED = (255, 48, 48)
#C_INTERFACE = (40,10,10)
C_INTERFACE = (10,25,60)
#C_INTERFACE = (36,52,72)

# Measurements
PAD_DIST = 10 # Pixels
FLAG_HEIGHT = 128 # Pixels
FLAG_WIDTH = 128 # Pixels
MAX_UNIT_GRAPHIC_SIZE = 43 # Pixels. Both dimensions are 43.
SMALL_UNIT_GRAPHIC_SIZE = int(MAX_UNIT_GRAPHIC_SIZE*0.7)
PROVINCE_MAP_WIDTH = 5632 # Pixels, width of provinces.bmp
PROVINCE_MAP_HEIGHT = 2048 # Pixels

NAV_BUTTON_HEIGHT = 50 # Pixels
NAV_BUTTON_BORDER_WIDTH = 4 # Thickness, in pixels
SMALL_BORDER_WIDTH = int(NAV_BUTTON_BORDER_WIDTH/4)
BATTLE_ENTRY_HEIGHT = 40 # Pixels
TIMELINE_WIDTH = 10
MINOR_TIME_LINE_WIDTH = 5
TIMELINE_POS = 5 # Number of positions above and below the timeline for text
MIN_TIMELINE_HEIGHT = NAV_BUTTON_HEIGHT # Height of the lowest timeline bar

BATTLE_CIRCLE_SCALING_FACTOR = 0.1
SEA_BATTLE_SCALING_FACTOR = 200 # Applied on top of the above number
