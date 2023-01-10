## EU4 War Explorer
created by jontiben

![eu4-war-explorer-demo](https://user-images.githubusercontent.com/25780026/211480392-eda28992-3b5e-4c65-aaa5-a14dadff79d1.png)


This application reads EU4 savefiles (ending in the file extension .eu4) for information about past wars and then presents it in an easily readable format. It features:
- A searchable list of every finished war in the savefile (searchable by elements of the war title or by tags involved)
- Breakdowns of the overall casualties in a war by side which can be further broken down by individual nation
- A list of battles fought in the war plotted on a map
- A breakdown of forces and losses for each battle
- A scrollable timeline showing major events over the course of the war
- Full mod support

Navigation is done exclusively through clicking, the ESC key, and typing to search on the war list screen.

Note that the first 11 wars on the battle screen will always be the same on any vanilla EU4 savefile because they took place before the beginning of the game.


Planned features are:
- The ability to sort wars and battles by total casualty count
- More information on the timeline
- Some sort of indicator whenever you can press ESC to return to a window

This project was written entirely in Python using Pygame and tkinter for the UI and PIL for modded map processing.

To contact me, please send me a friend request on discord where I am jontiben#7855.
