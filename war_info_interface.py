# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above
# copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

import pygame
import math
import defines
import common_functions
import debug_functions
#import random

#MAX_BATTLE_OFFSET = 8 # Max amount (in pixels on the original-scale map) to randomly offset the centerpoint of each
# battle to one side in order to avoid overlaps.

infantry_graphic = pygame.image.load(defines.INFANTRY_GRAPHIC)
cavalry_graphic = pygame.image.load(defines.CAVALRY_GRAPHIC)
artillery_graphic = pygame.image.load(defines.ARTILLERY_GRAPHIC)
tra_graphic = pygame.image.load(defines.TRA_GRAPHIC)
gal_graphic = pygame.image.load(defines.GAL_GRAPHIC)
ls_graphic = pygame.image.load(defines.LS_GRAPHIC)
hs_graphic = pygame.image.load(defines.HS_GRAPHIC)
all_graphics_list = [infantry_graphic, cavalry_graphic, artillery_graphic,
					hs_graphic, ls_graphic, gal_graphic, tra_graphic]
land_graphics_list = [infantry_graphic, cavalry_graphic, artillery_graphic]
sea_graphics_list = [hs_graphic, ls_graphic, gal_graphic, tra_graphic]

battle_type = "casualties"

def render_timeline(window, font, small_font, light_font, stats_font, present_date):
	window.fill(defines.C_INTERFACE)

	halfheight = int((window.get_height()-defines.NAV_BUTTON_HEIGHT)/2)

	start_days = common_functions.date_to_days(WAR.start_date)
	if not WAR.ongoing:
		war_length = common_functions.date_to_days(WAR.end_date) - start_days
	else:
		war_length = common_functions.date_to_days(present_date) - start_days
	timeline_length = war_length * defines.TIMELINE_LENGTH_MULTIPLIER
	timeline = pygame.draw.line(window, defines.C_GOLD, (defines.PAD_DIST-CURR_POSITION, halfheight), (timeline_length+defines.PAD_DIST-CURR_POSITION, halfheight), defines.TIMELINE_WIDTH)

	portion_distance = (window.get_height()-defines.NAV_BUTTON_HEIGHT)/(defines.TIMELINE_POS*2+1)

	to_render = []
	render_rects = []
	for e in range(len(WAR.events)):
		event = WAR.events[e]
		act_e = int(e/2)
		x_pos = ((event[0]-start_days)*defines.TIMELINE_LENGTH_MULTIPLIER)+defines.PAD_DIST-CURR_POSITION
		if -360 < x_pos < window.get_width():
			start_point = (x_pos, halfheight)
			if event[3] == "join" or event[3] == "quit":
				info_text = font.render(event[2], True, defines.C_LGRAY)
			elif event[3] == "battle":
				info_text = font.render(event[2], True, defines.C_RED)
			else:
				info_text = font.render(event[2], True, defines.C_WHITE)
			info_text_loc = info_text.get_rect()
			date_text = light_font.render(event[1], True, defines.C_LGRAY)
			date_text_loc = date_text.get_rect()
			if e % 2 == 0: # Above the line
				end_point = (x_pos, halfheight - (defines.TIMELINE_POS-(act_e % defines.TIMELINE_POS))*portion_distance + defines.PAD_DIST)
				info_text_loc.y = end_point[1]
				date_text_loc.y = info_text_loc.bottom-defines.PAD_DIST
			else: # Below the line
				end_point = (x_pos, halfheight + (defines.TIMELINE_POS-(act_e % defines.TIMELINE_POS))*portion_distance - defines.PAD_DIST)
				info_text_loc.bottom = end_point[1]
				date_text_loc.bottom = info_text_loc.y+defines.PAD_DIST
			info_text_loc.x = end_point[0] + defines.PAD_DIST
			date_text_loc.x = info_text_loc.x
			line = pygame.draw.line(window, defines.C_GOLD, start_point, end_point, defines.MINOR_TIME_LINE_WIDTH)

			render_rects.append((defines.C_INTERFACE, (info_text_loc.x-int(defines.PAD_DIST/2), info_text_loc.y, info_text_loc.width, info_text_loc.height)))
			render_rects.append((defines.C_INTERFACE, (date_text_loc.x-int(defines.PAD_DIST/2), date_text_loc.y, date_text_loc.width, date_text_loc.height)))
			to_render.append((info_text, info_text_loc))
			to_render.append((date_text, date_text_loc))

	for t in range(0, len(render_rects), 2):
		pygame.draw.rect(window, render_rects[t][0], render_rects[t][1])
		pygame.draw.rect(window, render_rects[t+1][0], render_rects[t+1][1])
		window.blit(to_render[t][0], to_render[t][1])
		window.blit(to_render[t+1][0], to_render[t+1][1])

	render_screen_buttons(window, font)
	pygame.display.update()


def render_map(window, font, small_font, light_font, stats_font, terrain_map, river_map, border_map, province_mids_path,
			   output_map = False):
	global MAP_SIZE
	window.fill(defines.C_INTERFACE)

	sized_terrain_map = pygame.transform.scale(terrain_map, (int(window.get_width()), 
		int((terrain_map.get_height()/terrain_map.get_width())*window.get_width())))
	window.blit(sized_terrain_map, (0, 0))
	sized_terrain_map_loc = sized_terrain_map.get_rect() # For convenience later

	if "rivers" in MAP_TYPES:
		sized_river_map = pygame.transform.scale(river_map, (int(window.get_width()),
			int((terrain_map.get_height()/terrain_map.get_width())*window.get_width())))
		window.blit(sized_river_map, (0, 0))

	if "borders" in MAP_TYPES:
		sized_borders_map = pygame.transform.scale(border_map, (int(window.get_width()), 
			int((terrain_map.get_height()/terrain_map.get_width())*window.get_width())))
		window.blit(sized_borders_map, (0, 0))


	province_dict = {}
	province_mids_file = open(province_mids_path,'r')
	lines = province_mids_file.readlines()

	for line in lines:
		line = line.split(',')
		province_dict[line[0]] = (float(line[1]), float(line[2]))
	province_mids_file.close()

	if BATTLE == None:
		battle_list = WAR.battles
		circle_color = defines.C_TRANS_ORANGE
	else:
		battle_list = [BATTLE]
		circle_color = defines.C_ORANGE

	latest_battle_days = 1
	first_battle_days = None
	if BATTLE is None:
		for battle in battle_list:
			current_battle_days = common_functions.date_to_days(battle.date)
			if first_battle_days == None:
				first_battle_days = current_battle_days
			if current_battle_days > latest_battle_days:
				latest_battle_days = current_battle_days
			if current_battle_days < first_battle_days:
				first_battle_days = current_battle_days
		latest_battle_days -= first_battle_days

	battle_center_size = defines.BATTLE_CENTER_SIZE
	date_color_size = defines.DATE_COLOR_SIZE
	if output_map:
		battle_center_size *= 2
		date_color_size *= 1.5
	for battle in battle_list:
		# Translucent circles scaled based on battle loss count

		curr_x = province_dict[battle.location][0]#+random.randint(-MAX_BATTLE_OFFSET,MAX_BATTLE_OFFSET)
		curr_y = province_dict[battle.location][1]#+random.randint(-MAX_BATTLE_OFFSET,MAX_BATTLE_OFFSET)
		mod_x = int(curr_x*(window.get_width()/MAP_SIZE[0]))
		mod_y = int(curr_y*(sized_terrain_map.get_rect().height/MAP_SIZE[1]))
		battle_surface = pygame.Surface((window.get_width(), window.get_height()), pygame.SRCALPHA)
		if battle.surface == "land":
			battle_scale = int(math.sqrt((battle.attacking_losses+battle.defending_losses)*defines.BATTLE_CIRCLE_SCALING_FACTOR))
			
		else: # Sea
			battle_scale = int(math.sqrt((battle.attacking_losses+battle.defending_losses)*defines.BATTLE_CIRCLE_SCALING_FACTOR*defines.SEA_BATTLE_SCALING_FACTOR))
		if battle_type == "date" and BATTLE is None:
			battle_days = common_functions.date_to_days(battle.date) - first_battle_days
			red = int((battle_days/latest_battle_days)*255)
			blue = int((1-(battle_days/latest_battle_days))*255)
			circle_color = (red, 0, blue, 220)

		if battle_type == "casualties":
			pygame.draw.circle(battle_surface, circle_color, (mod_x, mod_y), battle_scale)
		elif battle_type == "date":
			pygame.draw.circle(battle_surface, circle_color, (mod_x, mod_y), date_color_size)
		window.blit(battle_surface,(0, 0)) # Done individually to make the circles layer properly
		#battle_center_list.append([mod_x, mod_y, battle.surface])

	for battle in WAR.battles:
		curr_x = province_dict[battle.location][0]#+random.randint(-MAX_BATTLE_OFFSET,MAX_BATTLE_OFFSET)
		curr_y = province_dict[battle.location][1]#random.randint(-MAX_BATTLE_OFFSET,MAX_BATTLE_OFFSET)
		mod_x = int(curr_x*(window.get_width()/MAP_SIZE[0]))
		mod_y = int(curr_y*(sized_terrain_map.get_rect().height/MAP_SIZE[1]))
		if battle.surface == "land":
			pygame.draw.circle(window, defines.C_BLACK, (mod_x, mod_y), battle_center_size)
		else:
			pygame.draw.circle(window, defines.C_WHITE, (mod_x, mod_y), battle_center_size)
	if output_map:
		return window
	if not SOMETHING_FOCUSED:
		render_battles(window, font, small_font, light_font, stats_font, terrain_map)
	else:
		render_one_battle(window, font, small_font, light_font, stats_font, terrain_map)

def render_one_battle(window, font, small_font, light_font, stats_font, terrain_map):
	map_bottom = int((terrain_map.get_height()/terrain_map.get_width())*window.get_width())
	window.fill(defines.C_INTERFACE, (0, map_bottom, window.get_width(), window.get_height()-map_bottom))

	title_bar_loc = (0, map_bottom, window.get_width(), defines.NAV_BUTTON_HEIGHT)
	title_bar = pygame.draw.rect(window, defines.C_INTERFACE, title_bar_loc)
	title_bar_outline = pygame.draw.rect(window, defines.C_GOLD, title_bar_loc, defines.NAV_BUTTON_BORDER_WIDTH)
	space_before_battles = title_bar_loc[1] + defines.NAV_BUTTON_HEIGHT

	# Title of the battle
	battle_title = font.render(BATTLE.fullname, True, defines.C_WHITE)
	battle_title_loc = battle_title.get_rect()
	battle_title_loc.x = defines.PAD_DIST
	battle_title_loc.centery = title_bar.centery
	window.blit(battle_title, battle_title_loc)

	if BATTLE.surface == "land":
		surface_text = small_font.render("(land)", True, defines.C_BLACK)
	else:
		surface_text = small_font.render("(sea)", True, defines.C_WHITE)
	surface_text_loc = surface_text.get_rect()
	surface_text_loc.x = battle_title_loc.right+defines.PAD_DIST*4
	surface_text_loc.centery = battle_title_loc.centery
	window.blit(surface_text, surface_text_loc)

	# Date
	date_text = light_font.render(common_functions.date_conversion(BATTLE.date), True, defines.C_LGRAY)
	date_text_loc = date_text.get_rect()
	date_text_loc.right = window.get_width()-defines.PAD_DIST
	date_text_loc.centery = battle_title_loc.centery
	window.blit(date_text, date_text_loc)

	attacker_obj = WAR.participants[BATTLE.attacker]
	defender_obj = WAR.participants[BATTLE.defender]
	battle_flag_height = int(defines.FLAG_HEIGHT/2)
	battle_flag_width = int(defines.FLAG_WIDTH/2)

	start_of_battle_info = map_bottom+defines.NAV_BUTTON_HEIGHT

	# Battle attacker's flag
	att_flag = pygame.transform.scale(common_functions.load_flag(attacker_obj.name, WAR), (battle_flag_width, battle_flag_height))
	att_flag_loc = att_flag.get_rect()
	att_flag_loc.topleft = (defines.PAD_DIST, defines.PAD_DIST+start_of_battle_info)
	window.blit(att_flag, att_flag_loc)

	# Battle defender's flag
	def_flag = pygame.transform.scale(common_functions.load_flag(defender_obj.name, WAR), (battle_flag_width, battle_flag_height))
	def_flag_loc = def_flag.get_rect()
	def_flag_loc.topright = (window.get_width()-defines.PAD_DIST, defines.PAD_DIST+start_of_battle_info)
	window.blit(def_flag, def_flag_loc)

	# Battle attacker's name
	att_name = font.render(attacker_obj.longname, True, defines.C_WHITE)
	att_name_loc = att_name.get_rect()
	att_name_loc.topleft = (att_flag_loc.right+defines.PAD_DIST, defines.PAD_DIST+start_of_battle_info)
	window.blit(att_name, att_name_loc)

	# Battle defender's name
	def_name = font.render(defender_obj.longname, True, defines.C_WHITE)
	def_name_loc = def_name.get_rect()
	def_name_loc.topright = (def_flag_loc.left-defines.PAD_DIST, defines.PAD_DIST+start_of_battle_info)
	window.blit(def_name, def_name_loc)

	# The word "attacked"
	attacked = small_font.render("- attacked -", True, defines.C_LGRAY)
	attacked_loc = attacked.get_rect()
	attacked_loc.center = (int(window.get_width()/2), def_name_loc.centery)
	window.blit(attacked, attacked_loc)

	# Who won
	won = small_font.render("(won)", True, defines.C_GOLD)
	won_loc = won.get_rect()
	won_loc.bottom = def_flag_loc.bottom
	if BATTLE.result == "yes": # Attacker won
		won_loc.left = att_flag_loc.right+defines.PAD_DIST
		pygame.draw.rect(window, defines.C_GOLD, att_flag_loc, defines.NAV_BUTTON_BORDER_WIDTH)
	else:
		won_loc.right = def_flag_loc.left-defines.PAD_DIST
		pygame.draw.rect(window, defines.C_GOLD, def_flag_loc, defines.NAV_BUTTON_BORDER_WIDTH)
	window.blit(won, won_loc)

	# Attacking General/Admiral
	if BATTLE.attacking_general == "None":
		commander_name = "No commander"
	elif BATTLE.surface == "land":
		commander_name = "General "+BATTLE.attacking_general
	else:
		commander_name = "Admiral "+BATTLE.attacking_general
	att_commander = small_font.render(commander_name, True, defines.C_WHITE)
	att_commander_loc = att_commander.get_rect()
	att_commander_loc.topleft = (defines.PAD_DIST, att_flag_loc.bottom+defines.PAD_DIST)
	window.blit(att_commander, att_commander_loc)

	# Defending General/Admiral
	if BATTLE.defending_general == "None":
		commander_name = "No commander"
	elif BATTLE.surface == "land":
		commander_name = "General "+BATTLE.defending_general
	else:
		commander_name = "Admiral "+BATTLE.defending_general
	def_commander = small_font.render(commander_name, True, defines.C_WHITE)
	def_commander_loc = def_commander.get_rect()
	def_commander_loc.topright = (window.get_width()-defines.PAD_DIST, def_flag_loc.bottom+defines.PAD_DIST)
	window.blit(def_commander, def_commander_loc)

	# The phrase "Initial Forces:"
	initial_forces = font.render("Initial Forces:", True, defines.C_WHITE)
	initial_forces_loc = initial_forces.get_rect()
	initial_forces_loc.center = (int(window.get_width()/2), def_commander_loc.centery)
	window.blit(initial_forces, initial_forces_loc)

	# A line
	pygame.draw.line(window, defines.C_GOLD, (-10, def_commander_loc.bottom+defines.PAD_DIST), (window.get_width()+10, def_commander_loc.bottom+defines.PAD_DIST))

	if BATTLE.surface == "land":
		force_length = 3
	else:
		force_length = 4

	# Attacking Forces
	for u in range(force_length):
		if BATTLE.surface == "land":
			curr_graphic = pygame.transform.scale(land_graphics_list[u],(defines.SMALL_UNIT_GRAPHIC_SIZE, defines.SMALL_UNIT_GRAPHIC_SIZE))
		else:
			curr_graphic = pygame.transform.scale(sea_graphics_list[u],(defines.SMALL_UNIT_GRAPHIC_SIZE, defines.SMALL_UNIT_GRAPHIC_SIZE))	
		curr_graphic_loc = curr_graphic.get_rect()
		curr_graphic_loc.topleft = (defines.PAD_DIST, att_commander_loc.bottom+defines.PAD_DIST*2+(defines.SMALL_UNIT_GRAPHIC_SIZE+defines.PAD_DIST)*u)
		window.blit(curr_graphic, curr_graphic_loc)
		curr_count = stats_font.render(common_functions.break_up_large_numbers(BATTLE.attacking_force[u]), True, defines.C_WHITE)
		curr_count_loc = curr_count.get_rect()
		curr_count_loc.bottomleft = (curr_graphic_loc.right+defines.PAD_DIST, curr_graphic_loc.bottom)
		window.blit(curr_count, curr_count_loc)
	# Total
	att_total = stats_font.render(common_functions.break_up_large_numbers(sum(BATTLE.attacking_force)), True, defines.C_WHITE)
	att_total_loc = att_total.get_rect()
	att_total_loc.bottomleft = (defines.PAD_DIST*2+defines.SMALL_UNIT_GRAPHIC_SIZE, curr_graphic_loc.bottom+defines.SMALL_UNIT_GRAPHIC_SIZE+defines.PAD_DIST)
	window.blit(att_total, att_total_loc)
	# Losses
	att_losses = stats_font.render(common_functions.break_up_large_numbers(BATTLE.attacking_losses)+" losses", True, defines.C_WHITE)
	att_losses_loc = att_losses.get_rect()
	att_losses_loc.bottomleft = (att_total_loc.right+defines.PAD_DIST*4, att_total_loc.bottom)
	window.blit(att_losses, att_losses_loc)

	# Defending Forces
	for u in range(force_length):
		if BATTLE.surface == "land":
			curr_graphic = pygame.transform.scale(land_graphics_list[u],(defines.SMALL_UNIT_GRAPHIC_SIZE, defines.SMALL_UNIT_GRAPHIC_SIZE))
		else:
			curr_graphic = pygame.transform.scale(sea_graphics_list[u],(defines.SMALL_UNIT_GRAPHIC_SIZE, defines.SMALL_UNIT_GRAPHIC_SIZE))	
		curr_graphic_loc = curr_graphic.get_rect()
		curr_graphic_loc.topright = (window.get_width()-defines.PAD_DIST, att_commander_loc.bottom+defines.PAD_DIST*2+(defines.SMALL_UNIT_GRAPHIC_SIZE+defines.PAD_DIST)*u)
		window.blit(curr_graphic, curr_graphic_loc)
		curr_count = stats_font.render(common_functions.break_up_large_numbers(BATTLE.defending_force[u]), True, defines.C_WHITE)
		curr_count_loc = curr_count.get_rect()
		curr_count_loc.bottomright = (curr_graphic_loc.left-defines.PAD_DIST, curr_graphic_loc.bottom)
		window.blit(curr_count, curr_count_loc)
	# Total
	def_total = stats_font.render(common_functions.break_up_large_numbers(sum(BATTLE.defending_force)), True, defines.C_WHITE)
	def_total_loc = def_total.get_rect()
	def_total_loc.bottomright = (window.get_width()-defines.PAD_DIST*2-defines.SMALL_UNIT_GRAPHIC_SIZE, curr_graphic_loc.bottom+defines.SMALL_UNIT_GRAPHIC_SIZE+defines.PAD_DIST)
	window.blit(def_total, def_total_loc)
	# Losses
	def_losses = stats_font.render(common_functions.break_up_large_numbers(BATTLE.defending_losses)+" losses", True, defines.C_WHITE)
	def_losses_loc = def_losses.get_rect()
	def_losses_loc.bottomright = (def_total_loc.left-defines.PAD_DIST*4, def_total_loc.bottom)
	window.blit(def_losses, def_losses_loc)

	render_map_buttons(window, small_font, title_bar)

	pygame.display.update()

def render_battles(window, font, small_font, light_font, stats_font, terrain_map):
	global clickable_list

	map_bottom = int((terrain_map.get_height()/terrain_map.get_width())*window.get_width())
	window.fill(defines.C_INTERFACE, (0, map_bottom, window.get_width(), window.get_height()-map_bottom))

	title_bar_loc = (0, map_bottom, window.get_width(), defines.NAV_BUTTON_HEIGHT)
	title_bar = pygame.draw.rect(window, defines.C_INTERFACE, title_bar_loc)
	title_bar_outline = pygame.draw.rect(window, defines.C_GOLD, title_bar_loc, defines.NAV_BUTTON_BORDER_WIDTH)
	space_before_battles = title_bar_loc[1] + defines.NAV_BUTTON_HEIGHT
	
	war_title = font.render(WAR.title, True, defines.C_WHITE)
	war_title_loc = war_title.get_rect()
	war_title_loc.x = defines.PAD_DIST
	war_title_loc.centery = title_bar.centery
	window.blit(war_title, war_title_loc)

	battles_to_blit = []
	for i in range(CURR_POSITION, len(WAR.battles)):
		curr_battle = WAR.battles[i]
		i_loc = i - CURR_POSITION
		battle_title = font.render(curr_battle.fullname, True, defines.C_WHITE)
		battle_title_loc = battle_title.get_rect()
		battle_title_loc.x = defines.PAD_DIST
		battle_title_loc.y = i_loc * (defines.PAD_DIST + defines.BATTLE_ENTRY_HEIGHT) + space_before_battles
		battles_to_blit.append([battle_title, battle_title_loc])
		if curr_battle.surface == "land":
			surface_text = small_font.render("(land)", True, defines.C_BLACK)
		else:
			surface_text = small_font.render("(sea)", True, defines.C_WHITE)
		surface_text_loc = surface_text.get_rect()
		surface_text_loc.x = battle_title_loc.right+defines.PAD_DIST*4
		surface_text_loc.centery = battle_title_loc.centery
		battles_to_blit.append([surface_text, surface_text_loc])
		loss_text = stats_font.render(common_functions.break_up_large_numbers(str(curr_battle.attacking_losses+curr_battle.defending_losses))+" losses", True, defines.C_WHITE)
		loss_text_loc = loss_text.get_rect()
		loss_text_loc.right = int(window.get_width()*0.75)
		loss_text_loc.centery = battle_title_loc.centery
		battles_to_blit.append([loss_text, loss_text_loc])
		date_text = small_font.render(curr_battle.date, True, defines.C_LGRAY)
		date_text_loc = date_text.get_rect()
		date_text_loc.right = window.get_width() - defines.PAD_DIST
		date_text_loc.centery = battle_title_loc.centery
		battles_to_blit.append([date_text, date_text_loc])
		dividing_lines = pygame.draw.rect(window, defines.C_GOLD, (-10, battle_title_loc.y-2, window.get_width()+20, battle_title_loc.height+2), defines.SMALL_BORDER_WIDTH)
		clickable_list.append(["battle", curr_battle, dividing_lines])
	window.blits(battles_to_blit)

	render_screen_buttons(window, font)
	render_map_buttons(window, small_font, title_bar)

	pygame.display.update()

def render_map_buttons(window, small_font, title_bar):
	global clickable_list

	river_button_loc = (int(window.get_width()*0.5), title_bar.top+defines.PAD_DIST, defines.NAV_BUTTON_HEIGHT+defines.PAD_DIST*2, defines.NAV_BUTTON_HEIGHT-defines.PAD_DIST*2)
	if "rivers" in MAP_TYPES:
		river_backing = pygame.draw.rect(window, defines.C_LGRAY, river_button_loc)
		clickable_list.append(["unmap", "rivers", river_backing])
		river_toggle = pygame.draw.rect(window, defines.C_GOLD, river_button_loc, defines.NAV_BUTTON_BORDER_WIDTH)
	else:
		river_toggle = pygame.draw.rect(window, defines.C_GOLD, river_button_loc, defines.NAV_BUTTON_BORDER_WIDTH)
		clickable_list.append(["map", "rivers", river_toggle])
	river_label = small_font.render("RIVER", True, defines.C_GOLD)
	river_label_loc = river_label.get_rect()
	river_label_loc.center = river_toggle.center
	window.blit(river_label, river_label_loc)

	border_button_loc = (river_toggle.right+defines.PAD_DIST, title_bar.top+defines.PAD_DIST, defines.NAV_BUTTON_HEIGHT+defines.PAD_DIST*2, defines.NAV_BUTTON_HEIGHT-defines.PAD_DIST*2)
	if "borders" in MAP_TYPES:
		border_backing = pygame.draw.rect(window, defines.C_LGRAY, border_button_loc)
		clickable_list.append(["unmap", "borders", border_backing])
		border_toggle = pygame.draw.rect(window, defines.C_GOLD, border_button_loc, defines.NAV_BUTTON_BORDER_WIDTH)
	else:
		border_toggle = pygame.draw.rect(window, defines.C_GOLD, border_button_loc, defines.NAV_BUTTON_BORDER_WIDTH)
		clickable_list.append(["map", "borders", border_toggle])
	border_label = small_font.render("PROV.", True, defines.C_GOLD)
	border_label_loc = border_label.get_rect()
	border_label_loc.center = border_toggle.center
	window.blit(border_label, border_label_loc)

	battle_date_loc = (border_toggle.right+defines.PAD_DIST*4, title_bar.top+defines.PAD_DIST, defines.NAV_BUTTON_HEIGHT+defines.PAD_DIST*2, defines.NAV_BUTTON_HEIGHT-defines.PAD_DIST*2)
	if battle_type == "date":
		bd_backing = pygame.draw.rect(window, defines.C_LGRAY, battle_date_loc)
		clickable_list.append(["off_bd", "date", bd_backing])
		bd_toggle = pygame.draw.rect(window, defines.C_GOLD, battle_date_loc, defines.NAV_BUTTON_BORDER_WIDTH)
	else:
		bd_toggle = pygame.draw.rect(window, defines.C_GOLD, battle_date_loc, defines.NAV_BUTTON_BORDER_WIDTH)
		clickable_list.append(["on_bd", "date", bd_toggle])
	bd_label = small_font.render("DATE", True, defines.C_GOLD)
	bd_label_loc = bd_label.get_rect()
	bd_label_loc.center = bd_toggle.center
	window.blit(bd_label, bd_label_loc)

	export_loc = (bd_toggle.right+defines.PAD_DIST*4, title_bar.top+defines.PAD_DIST, defines.NAV_BUTTON_HEIGHT+defines.PAD_DIST*2, defines.NAV_BUTTON_HEIGHT-defines.PAD_DIST*2)
	export_toggle = pygame.draw.rect(window, defines.C_GOLD, export_loc, defines.NAV_BUTTON_BORDER_WIDTH)
	clickable_list.append(["export", "map", export_toggle])
	export_label = small_font.render("SAVE", True, defines.C_GOLD)
	export_label_loc = export_label.get_rect()
	export_label_loc.center = export_toggle.center
	window.blit(export_label, export_label_loc)


def render_screen_buttons(window, font):
	global clickable_list, current_screen

	button_height = defines.NAV_BUTTON_HEIGHT
	button_border_width = defines.NAV_BUTTON_BORDER_WIDTH
	
	# First Button
	button_loc1 = (0, window.get_height()-button_height, int(window.get_width()/2+1), button_height)
	pygame.draw.rect(window, defines.C_INTERFACE, button_loc1)
	button_rectangle1 = pygame.draw.rect(window, defines.C_GOLD, button_loc1, button_border_width)
	if current_screen == "info":
		button_str1 = "View Battles"
		clickable_list.append(["switch_window","battles",button_rectangle1])
	elif current_screen == "battles" or current_screen == "timeline":
		button_str1 = "View Stats"
		clickable_list.append(["switch_window","info",button_rectangle1])
	button_text1 = font.render(button_str1, True, defines.C_GOLD)
	button_text_loc1 = button_text1.get_rect()
	button_text_loc1.center = button_rectangle1.center
	window.blit(button_text1, button_text_loc1)

	# Second button
	button_loc2 = (int(window.get_width()/2), window.get_height()-button_height, int(window.get_width()/2+1), button_height)
	pygame.draw.rect(window, defines.C_INTERFACE, button_loc2)
	button_rectangle2 = pygame.draw.rect(window, defines.C_GOLD, button_loc2, button_border_width)
	if current_screen == "info" or current_screen == "battles":
		button_str2 = "View Timeline"
		clickable_list.append(["switch_window","timeline",button_rectangle2])
	elif current_screen == "timeline":
		button_str2 = "View Battles"
		clickable_list.append(["switch_window","battles",button_rectangle2])
	button_text2 = font.render(button_str2, True, defines.C_GOLD)
	button_text_loc2 = button_text2.get_rect()
	button_text_loc2.center = button_rectangle2.center
	window.blit(button_text2, button_text_loc2)

def render_war_stats(window, font, small_font, light_font, stats_font, padding_before_small_flags, tag):
	# nation=000 tells it to display stats for all war participants

	# The phrase "losses by side"
	if tag == "000":
		total_losses = font.render("Total Losses by Side (Attrition):", True, defines.C_WHITE)
	else:
		country_data = participants[tag]
		if WAR.participants[tag].side == "attack":
			total_losses = font.render(country_data.longname+" Losses/% of Total (Attrition):", True, defines.C_WHITE)
		else:
			total_losses = font.render(country_data.longname+" (Attrition) % of Total/Losses:", True, defines.C_WHITE)
	total_losses_loc = total_losses.get_rect()
	total_losses_loc.centerx = int(window.get_width()/2)
	total_losses_loc.top = padding_before_small_flags+defines.PAD_DIST*4
	window.blit(total_losses, total_losses_loc)

	# Total Losses
	loss_dist_from_edge_of_screen = int(window.get_width()/4)
	loss_dist_from_top_of_screen = total_losses_loc.bottom+defines.PAD_DIST

	# Attackers
	if tag == "000" or country_data.side == "attack":
		a_losses_to_blit = []
		if tag == "000":
			a_loss_list = WAR.a_loss_list
			attacker_losses = WAR.attacker_losses
			a_attrition_losses = WAR.a_attrition_losses
		else:
			a_loss_list = country_data.loss_list
			attacker_losses = country_data.losses
			a_attrition_losses = country_data.attrition_losses

		for a in range(len(a_loss_list)):
			curr_graphic = all_graphics_list[a]
			curr_graphic_loc = curr_graphic.get_rect()
			curr_graphic_loc.topleft = (loss_dist_from_edge_of_screen, loss_dist_from_top_of_screen+a*(defines.PAD_DIST+defines.MAX_UNIT_GRAPHIC_SIZE))
			a_loss_str = common_functions.break_up_large_numbers(str(a_loss_list[a]))
			if tag != "000":
				try:
					a_loss_str += '/'+str(round(a_loss_list[a]/WAR.a_loss_list[a]*100, 2))+'%'
				except ZeroDivisionError:
					pass
			if attacker_losses[a*3+1] > 0:
				a_loss_str += " ("+common_functions.break_up_large_numbers(str(attacker_losses[a*3+1]))+')'
			loss_text = stats_font.render(a_loss_str, True, defines.C_WHITE)
			loss_text_loc = loss_text.get_rect()
			loss_text_loc.topleft = (loss_dist_from_edge_of_screen+defines.MAX_UNIT_GRAPHIC_SIZE+defines.PAD_DIST, curr_graphic_loc.y)
			a_losses_to_blit += [[curr_graphic, curr_graphic_loc], [loss_text, loss_text_loc]]
		window.blits(a_losses_to_blit)
		# Attacker Total
		a_total_str = common_functions.break_up_large_numbers(str(sum(attacker_losses)))
		if tag != "000":
			try:
				a_total_str += '/'+str(round(sum(attacker_losses)/sum(WAR.attacker_losses)*100, 2))+"%"
			except ZeroDivisionError:
				pass
		a_total_str += " ("+common_functions.break_up_large_numbers(str(a_attrition_losses))+")"
		a_total_text = stats_font.render(a_total_str, True, defines.C_WHITE)
		a_total_text_loc = a_total_text.get_rect()
		a_total_text_loc.y = curr_graphic_loc.y+defines.MAX_UNIT_GRAPHIC_SIZE+defines.PAD_DIST
		a_total_text_loc.x = loss_dist_from_edge_of_screen
		window.blit(a_total_text, a_total_text_loc)

	# Defenders
	if tag == "000" or country_data.side == "defend":
		d_losses_to_blit = []
		if tag == "000":
			d_loss_list = WAR.d_loss_list
			defender_losses = WAR.defender_losses
			d_attrition_losses = WAR.d_attrition_losses
		else:
			d_loss_list = country_data.loss_list
			defender_losses = country_data.losses
			d_attrition_losses = country_data.attrition_losses

		for d in range(len(d_loss_list)):
			curr_graphic = all_graphics_list[d]
			curr_graphic_loc = curr_graphic.get_rect()
			curr_graphic_loc.topright = (window.get_width()-loss_dist_from_edge_of_screen, loss_dist_from_top_of_screen+d*(defines.PAD_DIST+defines.MAX_UNIT_GRAPHIC_SIZE))
			d_loss_str = common_functions.break_up_large_numbers(str(d_loss_list[d]))
			if tag != "000":
				try:
					d_loss_str = str(round(d_loss_list[d]/WAR.d_loss_list[d]*100, 2))+"%/"+d_loss_str
				except ZeroDivisionError:
					pass
			if defender_losses[d*3+1] > 0:
				d_loss_str = '('+common_functions.break_up_large_numbers(str(defender_losses[d*3+1]))+") "+d_loss_str
			loss_text = stats_font.render(d_loss_str, True, defines.C_WHITE)
			loss_text_loc = loss_text.get_rect()
			loss_text_loc.topright = (window.get_width()-(loss_dist_from_edge_of_screen+defines.MAX_UNIT_GRAPHIC_SIZE+defines.PAD_DIST), curr_graphic_loc.y)
			d_losses_to_blit += [[curr_graphic, curr_graphic_loc], [loss_text, loss_text_loc]]
		window.blits(d_losses_to_blit)
		# Defender Total
		d_total_str = common_functions.break_up_large_numbers(str(sum(defender_losses)))
		if tag != "000":
			try:
				d_total_str = str(round(sum(defender_losses)/sum(WAR.defender_losses)*100, 2))+"%/"+d_total_str
			except ZeroDivisionError:
				pass
		d_total_str = '('+common_functions.break_up_large_numbers(str(d_attrition_losses))+") "+d_total_str
		d_total_text = stats_font.render(d_total_str, True, defines.C_WHITE)
		d_total_text_loc = d_total_text.get_rect()
		d_total_text_loc.y = curr_graphic_loc.y+defines.MAX_UNIT_GRAPHIC_SIZE+defines.PAD_DIST
		d_total_text_loc.right = window.get_width()-loss_dist_from_edge_of_screen
		window.blit(d_total_text, d_total_text_loc)

	# The absolute total casualty count
	if tag == "000":
		abs_total_str = "Overall losses of "+common_functions.break_up_large_numbers(str(sum(attacker_losses[:9])+sum(defender_losses[:9])))+" men, "+common_functions.break_up_large_numbers(str(sum(attacker_losses[9:])+sum(defender_losses[9:])))+" ships"
		abs_total_text = stats_font.render(abs_total_str, True, defines.C_WHITE)
		abs_total_text_loc = abs_total_text.get_rect()
		abs_total_text_loc.midtop = (int(window.get_width()/2), d_total_text_loc.bottom+defines.PAD_DIST*4)
		window.blit(abs_total_text, abs_total_text_loc)

def render_war(window, font, small_font, light_font, stats_font, tag="000"):
	global clickable_list
	window.fill(defines.C_INTERFACE)

	# War title
	war_title = font.render(WAR.title, True, defines.C_WHITE)
	war_title_loc = war_title.get_rect()
	war_title_loc.center = (window.get_width()/2, 0)
	war_title_loc.y = defines.PAD_DIST
	window.blit(war_title, war_title_loc)

	flag_height = defines.FLAG_HEIGHT # I want to get these at runtime but sometimes the flags can't load
	flag_width = defines.FLAG_WIDTH

	# Primary Belligerants' Flags
	prim_att_flag = common_functions.load_flag(prim_att, WAR)
	prim_att_flag_loc = prim_att_flag.get_rect()
	prim_att_flag_loc.topleft = (defines.PAD_DIST, defines.PAD_DIST)
	window.blit(prim_att_flag, prim_att_flag_loc)
	clickable_list.append(["flag",prim_att,prim_att_flag_loc])
	if WAR.outcome == "2":
		pygame.draw.rect(window, defines.C_GOLD, prim_att_flag_loc, defines.NAV_BUTTON_BORDER_WIDTH)

	prim_def_flag = common_functions.load_flag(prim_def, WAR)
	prim_def_flag_loc = prim_def_flag.get_rect()
	prim_def_flag_loc.topleft = (window.get_width()-flag_width-defines.PAD_DIST, defines.PAD_DIST)
	window.blit(prim_def_flag, prim_def_flag_loc)
	clickable_list.append(["flag",prim_def,prim_def_flag_loc])
	if WAR.outcome == "3":
		pygame.draw.rect(window, defines.C_GOLD, prim_def_flag_loc, defines.NAV_BUTTON_BORDER_WIDTH)

	# Primary Attacker's Name
	prim_att_name = font.render(participants[prim_att].longname, True, defines.C_WHITE)
	prim_att_name_loc = prim_att_name.get_rect()
	prim_att_name_loc.y = (defines.PAD_DIST*2+flag_height)
	prim_att_name_loc.x = (defines.PAD_DIST)
	window.blit(prim_att_name, prim_att_name_loc)
	
	# Primary Defender's Name
	prim_def_name = font.render(participants[prim_def].longname, True, defines.C_WHITE)
	prim_def_name_loc = prim_def_name.get_rect()
	prim_def_name_loc.y = (defines.PAD_DIST*2+flag_height)
	prim_def_name_loc.right = (window.get_width()-defines.PAD_DIST)
	window.blit(prim_def_name, prim_def_name_loc)	

	# Dates of the war
	war_dates_text = common_functions.date_conversion(WAR.start_date)+" - "
	if not WAR.ongoing:
		war_dates_text += common_functions.date_conversion(WAR.end_date)
	else:
		war_dates_text += "present"
	war_dates = small_font.render(war_dates_text,True, defines.C_LGRAY)
	war_dates_loc = war_dates.get_rect()
	war_dates_loc.center = (window.get_width()/2, 0)
	war_dates_loc.y = (flag_height/2)
	window.blit(war_dates, war_dates_loc)

	# War outcome
	war_outcome_str = common_functions.lookup_outcome(WAR.outcome)
	war_outcome = small_font.render(war_outcome_str, True, defines.C_GOLD)
	war_outcome_loc = war_outcome.get_rect()
	war_outcome_loc.y = war_dates_loc.bottom+defines.PAD_DIST
	war_outcome_loc.centerx = int(window.get_width()/2)
	window.blit(war_outcome, war_outcome_loc)

	# Literally just the word "attacked"
	attacked = small_font.render("-  attacked  -", True, defines.C_LGRAY)	
	attacked_loc = attacked.get_rect()
	attacked_loc.center = (window.get_width()/2, prim_att_name_loc.center[1])
	window.blit(attacked, attacked_loc)

	# Other attackers
	flag_half_height = int(flag_height/2)
	flag_half_width = int(flag_width/2)
	padding_before_small_flags = flag_height+defines.PAD_DIST*3+prim_att_name_loc.height
	for a in range(CURR_POSITION, len(add_attackers)):
		a_loc = a-CURR_POSITION
		curr_flag = pygame.transform.scale(common_functions.load_flag(add_attackers[a], WAR), (flag_half_width, flag_half_height))
		curr_flag_loc = curr_flag.get_rect()
		curr_flag_loc.x = defines.PAD_DIST
		curr_flag_loc.y = (a_loc*(defines.PAD_DIST+flag_half_height))+padding_before_small_flags
		window.blit(curr_flag, curr_flag_loc)
		clickable_list.append(["flag",add_attackers[a],curr_flag_loc])

		a_text = small_font.render(participants[add_attackers[a]].longname, True, defines.C_WHITE)
		a_text_loc = a_text.get_rect()
		a_text_loc.top = int(a_loc*(flag_half_height+defines.PAD_DIST))+padding_before_small_flags
		a_text_loc.x = flag_half_width+defines.PAD_DIST*2
		window.blit(a_text, a_text_loc)
		date_string = ""
		if participants[add_attackers[a]].join_date != WAR.start_date:
			date_string += participants[add_attackers[a]].join_date+"-"
		if participants[add_attackers[a]].quit_date != WAR.end_date and not (WAR.ongoing and participants[add_attackers[a]].quit_date == "annexed"):
			# If participants are annexed during an ongoing war this won't be reflected in the war info screen. We have no way of knowing that until
			# the war is over.
			date_string += "-"+participants[add_attackers[a]].quit_date
		if date_string != "":
			date_string = date_string.replace("--",'-')
			a_date = small_font.render(date_string, True, defines.C_LGRAY)
			a_date_loc = a_date.get_rect()
			a_date_loc.bottom = int(a_loc*(flag_half_height+defines.PAD_DIST))+flag_half_height+padding_before_small_flags
			a_date_loc.x = flag_half_width+defines.PAD_DIST*2
			window.blit(a_date, a_date_loc)

	# Other defenders
	for d in range(CURR_POSITION, len(add_defenders)):
		d_loc = d-CURR_POSITION
		curr_flag = pygame.transform.scale(common_functions.load_flag(add_defenders[d], WAR), (flag_half_width, flag_half_height))
		curr_flag_loc = curr_flag.get_rect()
		curr_flag_loc.right = window.get_width() - defines.PAD_DIST
		curr_flag_loc.y = (d_loc*(defines.PAD_DIST+flag_half_height))+flag_height+defines.PAD_DIST*3+prim_def_name_loc.height
		window.blit(curr_flag, curr_flag_loc)
		clickable_list.append(["flag",add_defenders[d],curr_flag_loc])

		d_text = small_font.render(participants[add_defenders[d]].longname, True, defines.C_WHITE)
		d_text_loc = d_text.get_rect()
		d_text_loc.top = int(d_loc*(flag_half_height+defines.PAD_DIST))+padding_before_small_flags
		d_text_loc.right = window.get_width()-(flag_half_width+defines.PAD_DIST*2)
		window.blit(d_text, d_text_loc)
		date_string = ""
		if participants[add_defenders[d]].join_date != WAR.start_date:
			date_string += participants[add_defenders[d]].join_date+"-"
		if participants[add_defenders[d]].quit_date != WAR.end_date and not (WAR.ongoing and participants[add_defenders[d]].quit_date == "annexed"):
			date_string += "-"+participants[add_defenders[d]].quit_date
		if date_string != "":
			date_string = date_string.replace("--",'-')
			d_date = small_font.render(date_string, True, defines.C_LGRAY)
			d_date_loc = d_date.get_rect()
			d_date_loc.bottom = int(d_loc*(flag_half_height+defines.PAD_DIST))+flag_half_height+padding_before_small_flags
			d_date_loc.right = window.get_width()-(flag_half_width+defines.PAD_DIST*2)
			window.blit(d_date, d_date_loc)

	render_war_stats(window, font, small_font, light_font, stats_font, padding_before_small_flags, tag=tag)
	render_screen_buttons(window, font)

	pygame.display.update()



def export_map(map):
	from datetime import datetime
	filename = f"exported_maps/ewe_battles_{str(datetime.now().time()).replace(':','').split('.')[0]}.{defines.MAP_OUTPUT_FORMAT}"
	try:
		debug_functions.debug_out(f"Exporting map to image")
		pygame.image.save(map, filename)
		debug_functions.debug_out(f"Successfully exported map to file [{filename}]")
	except:
		debug_functions.debug_out(f"Exporting map failed", event_type="ERROR")



def info_loop(window, font, small_font, light_font, stats_font, terrain_map, river_map, border_map, province_mids_path, event, present_date, force_update=False):
	global clickable_list
	global battle_type
	global LOADED_TAG
	global SOMETHING_FOCUSED
	global current_screen
	global CURR_POSITION
	global BATTLE
	global MAP_TYPES
	if event != None:
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				if not SOMETHING_FOCUSED:
					return 1
				else:
					LOADED_TAG = "000"
					SOMETHING_FOCUSED = False
					BATTLE = None
					if current_screen == "battles":
						render_map(window, font, small_font, light_font,  stats_font, terrain_map, river_map, border_map, province_mids_path)
		elif event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 4: # 4 and 5 are the scroll wheel
				if current_screen == "timeline":
					if CURR_POSITION > defines.TIMELINE_SCROLL_SIZE-defines.PAD_DIST:
						CURR_POSITION -= defines.TIMELINE_SCROLL_SIZE
				else:
					if CURR_POSITION > defines.SCROLL_SIZE-1:
						CURR_POSITION -= defines.SCROLL_SIZE
			elif event.button == 5:
				if current_screen == "info": 
					if CURR_POSITION < max(WAR.attacker_count, WAR.defender_count)-defines.SCROLL_SIZE-1:
						CURR_POSITION += defines.SCROLL_SIZE
				elif current_screen == "battles":
					if CURR_POSITION < len(WAR.battles)-defines.SCROLL_SIZE-1:
						CURR_POSITION += defines.SCROLL_SIZE
				elif current_screen == "timeline":
					CURR_POSITION += defines.TIMELINE_SCROLL_SIZE
			elif event.button == 1:
				mouse_pos = pygame.mouse.get_pos()
				for button in clickable_list:
					if button[2].collidepoint(mouse_pos):
						if button[0] == "flag":
							LOADED_TAG = button[1]
							SOMETHING_FOCUSED = True
						elif button[0] == "battle":
							SOMETHING_FOCUSED = True
							BATTLE = button[1]
							render_map(window, font, small_font, light_font, stats_font, terrain_map, river_map, border_map, province_mids_path)
						elif button[0] == "switch_window":
							CURR_POSITION = 0
							SOMETHING_FOCUSED = False
							current_screen = button[1]
							if current_screen == "battles":
								render_map(window, font, small_font, light_font, stats_font, terrain_map, river_map, border_map, province_mids_path)
							break # Necessary to stop it flipping back and forth infinitely
						elif button[0] == "map":
							MAP_TYPES.append(button[1])
							render_map(window, font, small_font, light_font, stats_font, terrain_map, river_map, border_map, province_mids_path)
							break
						elif button[0] == "unmap":
							MAP_TYPES.pop(MAP_TYPES.index(button[1])) #.remove() doesn't work for some reason. I haven't slept in 28 hours.
							render_map(window, font, small_font, light_font, stats_font, terrain_map, river_map, border_map, province_mids_path)
							break
						elif button[0] == "on_bd":
							battle_type = "date"
							render_map(window, font, small_font, light_font, stats_font, terrain_map, river_map,
									   border_map, province_mids_path)
							break
						elif button[0] == "off_bd":
							battle_type = "casualties"
							render_map(window, font, small_font, light_font, stats_font, terrain_map, river_map,
									   border_map, province_mids_path)
							break
						elif button[0] == "export":
							export_window = pygame.Surface((MAP_SIZE))
							map = render_map(export_window, font, small_font, light_font, stats_font, terrain_map,
											 river_map, border_map, province_mids_path, output_map=True)
							export_map(map)
							break




		clickable_list = []
		if current_screen == "info":
			render_war(window, font, small_font, light_font, stats_font, tag=LOADED_TAG)
		elif current_screen == "battles":
			if force_update:
				render_map(window, font, small_font, light_font, stats_font, terrain_map, river_map, border_map, province_mids_path)
			else:
				if not SOMETHING_FOCUSED:
					render_battles(window, font, small_font, light_font, stats_font, terrain_map)
				else:
					render_one_battle(window, font, small_font, light_font, stats_font, terrain_map)
		elif current_screen == "timeline":
			render_timeline(window, font, small_font, light_font, stats_font, present_date)

		return None

def init(window, font, small_font, light_font, stats_font, terrain_map, river_map, border_map, war):
	global WAR, BATTLE
	global prim_att, prim_def, add_attackers, add_defenders, participants
	global SOMETHING_FOCUSED, LOADED_TAG
	global current_screen, clickable_list, CURR_POSITION
	global MAP_TYPES
	global MAP_SIZE

	clickable_list = []
	SOMETHING_FOCUSED = False
	CURR_POSITION = 0
	LOADED_TAG = "000"
	WAR = war
	BATTLE = None
	current_screen = "info" # Info or battles
	MAP_TYPES = []

	MAP_SIZE = (terrain_map.get_width(), terrain_map.get_height())

	participants = WAR.participants

	prim_att = WAR.primary_attacker
	prim_def = WAR.primary_defender
	add_attackers, add_defenders = [], []
	for p in WAR.participants.keys():
		if participants[p].side == "attack" and p != prim_att:
			add_attackers.append(p)
		elif participants[p].side == "defend" and p != prim_def:
			add_defenders.append(p)

	render_war(window, font, small_font, light_font, stats_font)

