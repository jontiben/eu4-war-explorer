EU4 Savefile Explorer
created by jontiben

This application reads EU4 savefiles (ending in the file extension .eu4) for information about past wars and then presents it in an easily readable format. It features:
- A searchable list of every finished war in the savefile (searchable by elements of the war title or by tags involved)
- Breakdowns of the overall casualties in a war by side which can be further broken down by individual nation
- A list of battles fought in the war plotted on a map
- A breakdown of forces and losses for each battle
- A scrollable timeline showing major events over the course of the war
Navigation is done exclusively through clicking, the ESC key, and typing to search on the war list screen.
Note that the first 11 warss on the battle screen will always be the same on any vanilla EU4 savefile because they took place before the beginning of the game.

The EU4 Savefile Explorer does not currently support mods which add, change, or move tags or province IDs. It will load modded savefiles and you can open war information
for wars that only include vanilla nations. For mods (such as Beyond Typus) that change the location of some province IDs the battle location given on the map may not
be accurate. A battle will not be marked on the map if its province id does not exist in EU4.

Planned features are:
- The ability to sort wars and battles by total casualty count
- More information on the timeline
- Better support for modded saves
- Some sort of indicator whenever you can press ESC to return to a window

This project was written entirely in Python using Pygame for the UI. Other external libraries used are math, codecs, re, os, zipfile (used for decompressing compressed
savefiles), tkinter (used for the file selection dialog), and datetime.

To contact me send me a friend request on discord where I am jontiben#7855.
