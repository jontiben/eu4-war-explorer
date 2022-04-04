import pygame
import defines, commonfunctions, debugfunctions

global prev_position, current_position
global has_rendered

VALID_CHARS = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n',
'o','p','q','r','s','t','u','v','w','x','y','z',
'-',' ','á','é','í','ó','ú','ä','ë','ï','ö','ü','â',
'0','1','2','3','4','5','6','7','8','9']

LISTING_HEIGHT = 50 # Height of the bars
RECT_OFFSET = defines.PAD_DIST # Distance the bars are spaced from one another

FLAG_HEIGHT = int(LISTING_HEIGHT-LISTING_HEIGHT*0.15)
FLAG_WIDTH = FLAG_HEIGHT # They're squares

has_rendered = False # To trigger rendering of the list when the program is first initialized. Kind of lazy.

prev_position = 0
current_position = 0 # The topmost bar in the list

NEW_WAR_LIST = None
MODE = "all" # "all" or "player" (types of nations shown)

SCROLL_SIZE = 2 # Amount each click of the scroll wheel moves the list

SEARCH_TEXT = ""

def draw_list_controls(window, font, small_font):
	global LIST_CONTROLS
	button_bar_height = defines.NAV_BUTTON_HEIGHT
	button_border_width = defines.NAV_BUTTON_BORDER_WIDTH

	# Background bar the buttons are all sitting on
	button_back_loc = (0, window.get_height()-button_bar_height, window.get_width(), button_bar_height)
	button_back = pygame.draw.rect(window, defines.C_INTERFACE, button_back_loc)
	button_back_rectangle = pygame.draw.rect(window, defines.C_GOLD, button_back_loc, button_border_width)
	
	button_width = defines.NAV_BUTTON_HEIGHT+defines.PAD_DIST*2

	# Button to only show wars involving current player nations
	# Text to the left of the button
	sort_by_player_str = "Current player nations:"
	sort_by_player = font.render(sort_by_player_str, True, defines.C_GOLD)
	sort_by_player_loc = sort_by_player.get_rect()
	sort_by_player_loc.midleft = (defines.PAD_DIST, button_back_rectangle.centery)
	window.blit(sort_by_player, sort_by_player_loc)
	# Button background and text
	player_button_loc = (sort_by_player_loc.right+defines.PAD_DIST, button_back_rectangle.top+defines.PAD_DIST, 
		button_width, defines.NAV_BUTTON_HEIGHT-defines.PAD_DIST*2)
	if MODE == "player":
		player_button_backing = pygame.draw.rect(window, defines.C_LGRAY, player_button_loc)
		LIST_CONTROLS.append(["disable", "playermode", player_button_backing])
		player_button_toggle = pygame.draw.rect(window, defines.C_GOLD, player_button_loc, button_border_width)
	else:
		player_button_toggle = pygame.draw.rect(window, defines.C_GOLD, player_button_loc, button_border_width)
		LIST_CONTROLS.append(["enable", "playermode", player_button_toggle])
	player_button_label = small_font.render("PLAY", True, defines.C_GOLD)
	player_button_label_loc = player_button_label.get_rect()
	player_button_label_loc.center = player_button_toggle.center
	window.blit(player_button_label, player_button_label_loc)

	# Button to open a new savefile
	open_button_loc = (window.get_width()-defines.PAD_DIST-button_width, button_back_rectangle.top+defines.PAD_DIST, 
		button_width, defines.NAV_BUTTON_HEIGHT-defines.PAD_DIST*2)
	open_button = pygame.draw.rect(window, defines.C_GOLD, open_button_loc, button_border_width)
	open_button_label = small_font.render("OPEN", True, defines.C_GOLD)
	open_button_label_loc = open_button_label.get_rect()
	open_button_label_loc.center = open_button.center
	window.blit(open_button_label, open_button_label_loc)
	LIST_CONTROLS.append(["open", "", open_button])

	# The search bar
	search_bar_info_str = "Search nations:"
	search_bar_info = font.render(search_bar_info_str, True, defines.C_GOLD)
	search_bar_info_loc = search_bar_info.get_rect()
	search_bar_info_loc.midleft = (player_button_toggle.right+defines.PAD_DIST, player_button_toggle.centery)
	window.blit(search_bar_info, search_bar_info_loc)
	
	search_bar_x = search_bar_info_loc.right+defines.PAD_DIST
	search_bar_loc = (search_bar_x, button_back.y+defines.PAD_DIST,
		open_button_label_loc.x-search_bar_x-(defines.PAD_DIST*2), button_back.height-(defines.PAD_DIST*2))
	search_bar = pygame.draw.rect(window, defines.C_GOLD, search_bar_loc, button_border_width)

	# Text in the search bar
	if SEARCH_TEXT == "":
		search_text = small_font.render("(type)", True, defines.C_LGRAY)
	else:
		search_text = small_font.render(SEARCH_TEXT, True, defines.C_WHITE)
	search_text_loc = search_text.get_rect()
	search_text_loc.midleft = (search_bar.x+defines.PAD_DIST, search_bar.centery)
	window.blit(search_text, search_text_loc)


def list_disp_update(window, font, small_font, war_list):
	global prev_position, current_position, CLICKABLE_LIST, LIST_CONTROLS
	CLICKABLE_LIST = []
	LIST_CONTROLS = []
	MAX_COUNT = int(window.get_height()/(LISTING_HEIGHT+RECT_OFFSET+0.0)+1)
	window.fill(defines.C_BLACK)
	to_render = []
	for i in range(current_position, current_position+MAX_COUNT):
		if i < len(war_list):
			if war_list[i].viable == True:
				render_i = i-current_position
				curr_loc_rect = (0, render_i*(LISTING_HEIGHT+RECT_OFFSET), window.get_width(), LISTING_HEIGHT)
				curr_bar = pygame.draw.rect(window, defines.C_INTERFACE, curr_loc_rect)	
				# Render bars with the war title
				curr_text = font.render(war_list[i].title, True, defines.C_WHITE)
				text_loc = curr_text.get_rect()
				text_loc.center = (window.get_width()//2, render_i*(LISTING_HEIGHT+RECT_OFFSET)+(LISTING_HEIGHT/2))
				to_render.append((curr_text, text_loc))
				CLICKABLE_LIST.append(["war", war_list[i], curr_bar])

				# Render the start date on the left
				start_date_text = font.render(war_list[i].start_date, True, defines.C_LGRAY)
				start_text_loc = start_date_text.get_rect()
				start_text_loc.center = (0, render_i*(LISTING_HEIGHT+RECT_OFFSET)+(LISTING_HEIGHT/2))
				start_text_loc.x = defines.PAD_DIST
				to_render.append((start_date_text, start_text_loc))

				# Render the end date on the right
				end_date_text = font.render(war_list[i].end_date, True, defines.C_LGRAY)
				end_text_loc = end_date_text.get_rect()
				end_text_loc.center = (0, render_i*(LISTING_HEIGHT+RECT_OFFSET)+(LISTING_HEIGHT/2))
				end_text_loc.right = window.get_width()-defines.PAD_DIST
				to_render.append((end_date_text, end_text_loc))

				# Draw flags: (primary) attacker's left of the war title, defender's right
				if not commonfunctions.is_created_nation(war_list[i].participants[war_list[i].primary_attacker].name):
					# Can't load a flag that was generated while playing the save
					try:
						first_flag = pygame.transform.scale(pygame.image.load(war_list[i].participants[war_list[i].primary_attacker].flag_path), (FLAG_WIDTH, FLAG_HEIGHT))
					except:
						debugfunctions.debug_out(f"Failed to open flag for primary attacker {war_list[i].primary_attacker}",event_type="WARN")
						first_flag = pygame.transform.scale(pygame.image.load(defines.PATH_TO_BACKUP_FLAG), (FLAG_WIDTH, FLAG_HEIGHT))
				else:
					first_flag = pygame.transform.scale(pygame.image.load(defines.PATH_TO_BACKUP_FLAG), (FLAG_WIDTH, FLAG_HEIGHT))
				to_render.append((first_flag, (text_loc.left-defines.PAD_DIST-FLAG_WIDTH, text_loc.y)))	
				if not commonfunctions.is_created_nation(war_list[i].participants[war_list[i].primary_defender].name):
					try:
						second_flag = pygame.transform.scale(pygame.image.load(war_list[i].participants[war_list[i].primary_defender].flag_path), (FLAG_WIDTH, FLAG_HEIGHT))
					except:
						debugfunctions.debug_out(f"Failed to open flag for primary defender {war_list[i].primary_defender}",event_type="WARN")
						second_flag = pygame.transform.scale(pygame.image.load(defines.PATH_TO_BACKUP_FLAG), (FLAG_WIDTH, FLAG_HEIGHT))
				else:
					second_flag = pygame.transform.scale(pygame.image.load(defines.PATH_TO_BACKUP_FLAG), (FLAG_WIDTH, FLAG_HEIGHT))
				to_render.append((second_flag, (text_loc.right+defines.PAD_DIST, text_loc.y)))

	window.blits(to_render)
	draw_list_controls(window, font, small_font)
	pygame.display.update()

def get_player_war_list(war_list):
	new_list = []
	for war in war_list:
		if war.has_player:
			new_list.append(war)
	return new_list

def list_loop(window, font, small_font, war_list, event, force_update=False):
	global prev_position, current_position
	global has_rendered
	global MODE
	global NEW_WAR_LIST, SEARCH_TEXT
	prev_position = current_position
	changed_text = False
	if NEW_WAR_LIST == None:
		NEW_WAR_LIST = war_list
	if event != None:
		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 4: # 4 and 5 are the scroll wheel
				if current_position > SCROLL_SIZE-1:
					current_position -= SCROLL_SIZE
			elif event.button == 5:
				if current_position < len(NEW_WAR_LIST)-SCROLL_SIZE-1	:
					current_position += SCROLL_SIZE
			elif event.button == 1:
				mouse_pos = pygame.mouse.get_pos()
				for button in LIST_CONTROLS:
					if button[2].collidepoint(mouse_pos):
						if button[0] == "enable":
							if button[1] == "playermode":
								MODE = "player"
								NEW_WAR_LIST = get_player_war_list(war_list)
								changed_text = True
						elif button[0] == "disable":
							if button[1] == "playermode":
								MODE = "all"
								NEW_WAR_LIST = war_list
								changed_text = True
						elif button[0] == "open":
							current_position = 0
							return "open"
						current_position = 0
						force_update = True
						break
				if mouse_pos[1] < window.get_height() - defines.NAV_BUTTON_HEIGHT: # Off the button bar on the bottom
					for button in CLICKABLE_LIST:
						if button[2].collidepoint(mouse_pos):
							if button[0] == "war":
								return button[1]
				### Have options to sort by total casualty count
		elif event.type == pygame.KEYDOWN:
			if event.unicode in VALID_CHARS:
				SEARCH_TEXT += event.unicode.upper()
			elif event.key == 8: # Backspace
				SEARCH_TEXT = SEARCH_TEXT[:-1]
			elif event.key == 127: # DEL (deletes everything)
				SEARCH_TEXT = ""
			force_update = True
			changed_text = True

	# Update war list for search string
	if changed_text == True:
		if MODE == "player":
			# Search only player nations
			temp_war_list = get_player_war_list(war_list)
		else:
			temp_war_list = war_list
		NEW_WAR_LIST = []
		for war in temp_war_list:
			if SEARCH_TEXT in war.title.upper():
				NEW_WAR_LIST.append(war)
			else:
				for participant in war.participants:
					if SEARCH_TEXT in war.participants[participant].longname.upper():
						NEW_WAR_LIST.append(war)
					else:
						if SEARCH_TEXT == war.participants[participant].name.upper():
							NEW_WAR_LIST.append(war)

	if prev_position != current_position or force_update or not has_rendered:
		# Only render if the position has changed (scrolled), main.py wants to force it to (when
		# the window is resized), or the program has just initialized.
		has_rendered = True

		list_disp_update(window, font, small_font, NEW_WAR_LIST)
	return None