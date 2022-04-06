import codecs
import re
import os
import zipfile

import commonfunctions
import debugfunctions
import defines

alt_names = {} # Dictionary of names for countries created at runtime

### Currently doesn't handle active/ongoing wars

class Battle:
	def __init__(self, line_loc, name, surface, date, location, result, iteration,
		attacker, attacking_force: list, attacking_losses: int, attacking_general,
		defender, defending_force: list, defending_losses: int, defending_general):
		
		self.name = name
		self.surface = surface # "land" or "sea"
		self.date = date
		self.location = location # Province ID
		self.result = result # "yes" = attacker won, "no" = defender won
		self.iteration = iteration+' ' # Number of battle (1st, 2nd, 3rd, etc.) fought with the same name in this war
		# Plus a space because I'm lazy
		self.fullname = "NONE"

		self.attacker = attacker # A tag
		# Below is formatting a list of length 3 (originally cav, art, inf) for land battles, 
		# 4 (originally galley, light, heavy, trans) for naval battles
		# Those are transposed to [inf, cav, art] and [heavy, light, galley, trans] respectively
		if len(attacking_force) == 3:
			self.attacking_force = [attacking_force[2], attacking_force[0], attacking_force[1]]
		else:
			self.attacking_force = [attacking_force[2], attacking_force[1], attacking_force[0], attacking_force[3]]
		self.attacking_losses = attacking_losses # Integer
		self.attacking_general = attacking_general
		if self.attacking_general == "":
			self.attacking_general = "None"

		self.defender = defender
		if len(defending_force) == 3:
			self.defending_force = [defending_force[2], defending_force[0], defending_force[1]]
		else:
			self.defending_force = [defending_force[2], defending_force[1], defending_force[0], defending_force[3]]
		self.defending_losses = defending_losses
		self.defending_general = defending_general
		if self.defending_general == "":
				self.defending_general = "None"

	def update_name(self, other_battles):
		instances = 0
		for battle in other_battles:
			if battle == self.name:
				instances += 1

		if self.iteration == "1st " and instances < 2:
			self.iteration = ""

		if self.surface == "land":
			self.fullname = self.iteration+"Battle of "+self.name
		else:
			words = self.name.split(' ')
			if words[-1] != "Bay" and words[-1] != "Island" and words[0] != "Cape" and words[-1] != "Bank":
				self.fullname = self.iteration+"Battle of the "+self.name
			else:
				self.fullname = self.iteration+"Battle of "+self.name

		#if self.fullname == "NONE":
		#	debugfunctions.debug_out(f"No name found for battle at line {str(line_loc)}", event_type="WARN")


class Participant:
	def __init__(self, war_name, name, side, join_date, quit_date=None, level="secondary", losses=None, warscore=None):
		global alt_names
		self.war_name = war_name

		self.name = name # Nation's tag
		self.side = side # "attack" or "defend"
		self.level = level # "primary" or "secondary"
		self.warscore = warscore
		self.join_date = join_date
		self.quit_date = quit_date
		self.losses = losses

		self.flag_path = defines.PATH_TO_FLAGS_FOLDER+'/'+name+".tga"

		# Setting up the full name for the nation
		self.longname = None
		if not commonfunctions.is_created_nation(self.name):
			self.longname = commonfunctions.get_full_country_name(self.name)
		else: # Easier to handle this in here than in commonfunctions.py because the savefile is already open
			if self.name in alt_names.keys():
				if alt_names[self.name] == None:
					self.longname = self.name
				else:
					self.longname = alt_names[self.name]
			elif self.name[0] == 'F': # Tribal Federation
				if self.level == "primary" and self.side == "attack": ### Confirm works
					self.longname = war_name.split(' ')[1]+' '+war_name.split(' ')[2]
				else:
					self.longname = "Federation"
			if self.longname == None:
				# Last resort
				if "against" in war_name and side == "defend" and level == "primary":
					self.longname = war_name.split("against ")[-1]
				else:
					debugfunctions.debug_out(f"Couldn't find full name for tag {self.name}. This usually means that it's a colonial nation that's been annexed. Defaulting to tag.", event_type="WARN")
					self.longname = self.name
					alt_names[name] = None # Usually when a colonial nation has been annexed
		self.longname = self.longname[0].upper()+self.longname[1:]
		self.check_dates()

	def check_dates(self) -> None:
		# *Occasionally* participants slip through with no self.quit_date
		# This is probably because they were annexed in a separate peace
		self.quit_date = "annexed"
		### I wonder if there's an easy way to recover the date on which they were annexed?
		### ... I don't think so.

		# Sometimes this happens too?
		if self.join_date == None:
			self.join_date = "unknown"
			debugfunctions.debug_out(f"Couldn't find join date for {self.name} in war [{self.war_name}]", event_type="WARN")

	def consolidate_losses(self) -> None: 
		try: 
			self.losses = [int(j) for j in
			self.losses] 
		except: 
			self.losses = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		# HOW LOSSES WORK: (as far as I can tell)
		# Example: 11403 7835 0 1265 2756 0 8000 5671 0 0 0 0 2 0 0 0 0 0 0 0 0
		# It's broken into groups of three digits. The first three are infantry, second cavalry, third artillery,
		# fourth heavy ships, fifth light ships, sixth galleys, seventh transports. The first number in a group
		# refers to the number lost in combat, the second to attrition, and I'm not sure about the third (I've
		# never seen it anything other than 0)
		# That same loss line broken up:
		# inf: [11,403; 7,835*; 0] cav: [1,265; 2,756*; 0] art: [8,000; 5,671*; 0] hs: [0; 0*; 0]
		# ls: [2; 0*; 0] gal:[0; 0*; 0] tra:[0; 0*; 0] (attrition has the asterisk)
		loss = self.losses # Just for convenience
		self.inf_losses = sum(loss[:3])
		self.cav_losses = sum(loss[3:6])
		self.art_losses = sum(loss[6:9])
		self.hs_losses = sum(loss[9:12])
		self.ls_losses = sum(loss[12:15])
		self.gal_losses = sum(loss[15:18])
		self.tra_losses = sum(loss[18:21])
		self.loss_list = [self.inf_losses, self.cav_losses, self.art_losses, self.hs_losses, self.ls_losses, self.gal_losses, self.tra_losses]
		self.attrition_losses = sum([loss[i] for i in range(len(loss)) if (i+2) % 3 == 0])


class War:
	def __init__(self, start_point: int, end_point: int):

		self.viable = True # If there's a problem with the data provided in the save file (e.g. no participants in the Ottoman-Albanian war)
		# this can be set to false.

		self.start_point = start_point # First line of the war (should look like "previous_war={")
		self.end_point = end_point # Line with the war's closing bracket

		# Initializing variables to None so you can easily see what this function is supposed to set
		self.cassus_belli = None
		self.cb_target = None
		self.outcome = None
		self.start_date = "None"
		self.end_date = "None"
		# OUTCOMES:
		# 1 - draw
		# 2 - victory for attackers
		# 3 - victory for defenders
		self.attack_total_warscore = 0 # total attacker warscore
		self.defend_total_warscore = 0
		self.has_player = False # Includes a current player nation
		self.events = [] # List of tuples: (days, date, event)
		self.primary_attacker = "000"
		self.primary_defender = "000"

		self.battles = [] # All the battles recorded for the war, in chronological order
		
		self.title = get_line_data(start_point+1)
		if self.title == "":
			self.viable = False # For some reason the game generates 0-length wars with no participants early on
			# in the list of historical wars. These don't have titles.
			debugfunctions.debug_out(f"Empty war (no title, zero-length) found at line {str(start_point+1)}. Skipping war.",event_type="WARN")
			return

		self.participants = {}

		# Setting the start and end points for the "history" section ("history={")
		self.history_start = self.start_point + 2
		self.history_end = define_bracket_block(self.history_start)

		# Creating the participant classes in self.participants
		# (A dictionary indexed by the tag of the participant)
		# Setting their participants, sides, and join/quit dates
		# Example Text:
		#	1577.12.14={
		#		add_attacker="MJZ"
		#	}
		self.attacker_count = 0
		self.defender_count = 0
		for check_date_num in range(self.history_start+1, self.history_end):
			if is_date(check_date_num):
				for check_action_num in range(check_date_num+1,define_bracket_block(check_date_num)):
					if clean_tabs(check_action_num)[:3] == "add":
						if "attacker" in clean_tabs(check_action_num):
							self.attacker_count += 1
							self.participants[get_line_data(check_action_num)] = Participant(self.title, get_line_data(check_action_num),"attack",clean_date(check_date_num))
						else:
							self.defender_count += 1
							self.participants[get_line_data(check_action_num)] = Participant(self.title, get_line_data(check_action_num),"defend",clean_date(check_date_num))
					elif clean_tabs(check_action_num)[:3] == "rem":
						try:
							self.participants[get_line_data(check_action_num)].quit_date = clean_date(check_date_num)
						except LookupError: # Nation is created while the war is going and never gets an entry for joining
							self.participants[get_line_data(check_action_num)] = Participant(self.title, get_line_data(check_action_num),"attack",None,quit_date=clean_date(check_date_num))

		# Adding other info to participants
		for check_participants_num in range(self.history_end,self.end_point):
			if clean_tabs(check_participants_num)[:12] == "participants":
				curr_tag = get_line_data(check_participants_num+2)
				self.participants[curr_tag].warscore = float(get_line_data(check_participants_num+1))
				if self.participants[curr_tag].side == "attack":
					self.attack_total_warscore += float(get_line_data(check_participants_num+1))
				else:
					self.defend_total_warscore += float(get_line_data(check_participants_num+1))
				self.participants[curr_tag].losses = get_line_data(check_participants_num+5)[:-1].split(' ')
				self.participants[curr_tag].consolidate_losses()
		for key in self.participants.keys():
			if self.participants[key].name in PLAYER_COUNTRIES:
				self.has_player = True
				break

		# Miscellaneous war info
		for check_misc_num in range(self.history_end,self.end_point):
			if "cassus_belli" in file_lines[check_misc_num]:
				self.cassus_belli = get_line_data(check_misc_num)
				self.cb_target = get_line_data(check_misc_num-1)
			if "original_" in file_lines[check_misc_num]:
				try:
					self.participants[get_line_data(check_misc_num)].level = "primary"
				except LookupError:
					self.viable = False
					debugfunctions.debug_out(f"Primary participant {get_line_data(check_misc_num)} not in [{self.title}] participants list (bad participant on line {str(check_misc_num)}). Skipping war.",event_type="WARN")
			if "outcome" in file_lines[check_misc_num]:
				self.outcome = get_line_data(check_misc_num)

		if self.viable == True:
			# Other init functions, split off for readability.
			self.set_primary_participants()
			self.find_battles()
			self.get_total_losses()
			self.get_events()

		if self.viable == True:
			original_attacker = None
			for check_original_attacker_num in range(self.history_end,self.end_point):
				if get_line_key(check_original_attacker_num) == "original_attacker=":
					original_attacker = get_line_data(check_original_attacker_num)
					break

			if original_attacker != None:
				self.start_date = self.participants[original_attacker].join_date
				self.end_date = self.participants[original_attacker].quit_date
			else:
				debugfunctions.debug_out(f"No original attacker found for war [{self.title}]. Skipping war.",event_type="WARN")
		

	def get_events(self) -> None:
		try:
			start_days = commonfunctions.date_to_days(self.start_date)
			end_days = commonfunctions.date_to_days(self.end_date)
			self.events.append((start_days, self.start_date, self.participants[self.primary_attacker].longname+" declared war on "+self.participants[self.primary_defender].longname, "start"))
			self.events.append((end_days, self.end_date, "War ended", "end"))
			for participant in self.participants.keys():
				curr_join_days = commonfunctions.date_to_days(self.participants[participant].join_date)
				curr_quit_days = commonfunctions.date_to_days(self.participants[participant].quit_date)
				if curr_join_days-start_days > 1:
					self.events.append((curr_join_days, self.participants[participant].join_date, self.participants[participant].side+"er "+self.participants[participant].longname+" joined the war", "join"))
				if curr_quit_days != end_days:
					self.events.append((curr_quit_days, self.participants[participant].quit_date, self.participants[participant].side+"er "+self.participants[participant].longname+" left the war", "quit"))
			for battle in self.battles:
				self.events.append((commonfunctions.date_to_days(battle.date), battle.date, battle.fullname, "battle"))

			self.events.sort(key=first_element)
		except Exception as exception:
			self.viable = False
			debugfunctions.debug_out(f"Exception [{exception}] occurred when building event list for [{self.title}]. Skipping war.",event_type="WARN")

	def find_battles(self) -> None: 
		for check_battle_num in range(self.history_start,self.history_end):
			if clean_tabs(check_battle_num) == "battle={":
				battle_date = clean_date(check_battle_num-1)
				battle_start_point = check_battle_num
				battle_end_point = define_bracket_block(check_battle_num)
				attacker_info = []
				defender_info = []
				for n in range(battle_start_point, battle_end_point):
					if get_line_key(n) == "name=":
						battle_name = get_line_data(n)
						curr_iteration = 1
						for b in range(len(self.battles)):
							if self.battles[b].name == battle_name:
								curr_iteration += 1
						battle_iteration = commonfunctions.return_ordinal_number(str(curr_iteration))
					elif get_line_key(n) == "location=":
						battle_location = get_line_data(n)
					elif get_line_key(n) == "result=":
						battle_result = get_line_data(n)
					elif clean_tabs(n) == "attacker={":
						attacker_info = parse_combatant_block(n, define_bracket_block(n))
					elif clean_tabs(n) == "defender={":
						defender_info = parse_combatant_block(n, define_bracket_block(n))
				if len(attacker_info) > 0: # Just in case a battle only has one combatant saved. It'll still break a few lines down so this is kind of pointless.
					battle_surface = attacker_info[0]
				else:
					battle_surface = defender_info[0]
				self.battles.append(Battle(check_battle_num, battle_name, battle_surface, battle_date, battle_location, battle_result, battle_iteration,
					attacker_info[3], attacker_info[1], attacker_info[2], attacker_info[4],
					defender_info[3], defender_info[1], defender_info[2], defender_info[4]))
		battle_name_list = []
		for battle in self.battles:
			battle_name_list.append(battle.name)
		for battle_obj in self.battles:
			battle_obj.update_name(battle_name_list)

	def set_primary_participants(self):
		for participant in self.participants.keys():
			if self.participants[participant].level == "primary": # Find the first attacker with the level "primary"
				if self.participants[participant].side == "attack":
					self.primary_attacker = participant
				elif self.participants[participant].side == "defend":
					self.primary_defender = participant

	def get_total_losses(self):
		# Does a bunch of arithmetic
		# Also cleans up nations that have had no losses added
		self.attacker_losses = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,]
		self.defender_losses = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,]
		for participant in self.participants.keys():
			if self.participants[participant].losses == None:
				self.participants[participant].losses = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,]
			if self.participants[participant].side == "attack":
				for element in range(len(self.participants[participant].losses)):
					self.attacker_losses[element] += self.participants[participant].losses[element]
			elif self.participants[participant].side == "defend":
				for element in range(len(self.participants[participant].losses)):
					self.defender_losses[element] += self.participants[participant].losses[element]
	
		loss = self.attacker_losses
		self.a_inf_losses = sum(loss[:3])
		self.a_cav_losses = sum(loss[3:6])
		self.a_art_losses = sum(loss[6:9])
		self.a_hs_losses = sum(loss[9:12])
		self.a_ls_losses = sum(loss[12:15])
		self.a_gal_losses = sum(loss[15:18])
		self.a_tra_losses = sum(loss[18:21])
		self.a_loss_list = [self.a_inf_losses, self.a_cav_losses, self.a_art_losses, self.a_hs_losses, self.a_ls_losses, self.a_gal_losses, self.a_tra_losses]
		self.a_attrition_losses = sum([loss[i] for i in range(len(loss)) if (i+2) % 3 == 0])

		loss = self.defender_losses
		self.d_inf_losses = sum(loss[:3])
		self.d_cav_losses = sum(loss[3:6])
		self.d_art_losses = sum(loss[6:9])
		self.d_hs_losses = sum(loss[9:12])
		self.d_ls_losses = sum(loss[12:15])
		self.d_gal_losses = sum(loss[15:18])
		self.d_tra_losses = sum(loss[18:21])
		self.d_loss_list = [self.d_inf_losses, self.d_cav_losses, self.d_art_losses, self.d_hs_losses, self.d_ls_losses, self.d_gal_losses, self.d_tra_losses]
		self.d_attrition_losses = sum([loss[i] for i in range(len(loss)) if (i+2) % 3 == 0])


def parse_combatant_block(start_point: int, end_point: int) -> list: 
	# Returns a list:
	# [surface, [force], losses, tag, general name]
	ground_forces = {"cavalry": 0, "artillery": 0, "infantry": 0}  
	sea_forces = {"galley": 0, "light_ship": 0, "heavy_ship": 0, "transport": 0}
	# Dictionaries allow you to make the combatants always stick to the same order in the list output on the other side.
	out_list = []
	for o in range(start_point, end_point):
		current_keyword = get_line_key(o).replace('=',"")
		if current_keyword in ground_forces.keys():
			battle_surface = "land"
			ground_forces[current_keyword] = int(get_line_data(o))
		elif current_keyword in sea_forces.keys():
			battle_surface = "sea"
			sea_forces[current_keyword] = int(get_line_data(o))
		elif current_keyword == "losses":
			battle_losses = int(get_line_data(o))
		elif current_keyword == "country":
			battle_country = get_line_data(o)
		elif current_keyword == "commander":
			battle_commander = get_line_data(o)

	out_list.append(battle_surface)
	if battle_surface == "land":
		out_list.append(list(ground_forces.values()))
	elif battle_surface == "sea":
		out_list.append(list(sea_forces.values()))
	out_list.append(battle_losses)
	out_list.append(battle_country)
	out_list.append(battle_commander)

	return out_list


# The following are mostly utility functions.
def first_element(input_list: list):
	return input_list[0]


def is_date(line_no: int) -> bool:
	# Determines if the data in a given line is a properly-formatted date
	line = clean_date(line_no)
	if re.fullmatch(r"\d{4}.\d\d?.\d\d?",line) != None:
		return True
	return False


def clean_tabs(line_no: int) -> str:
	return file_lines[line_no].replace('	',"")


def get_line_data(line_no: int) -> str:
	# Clears away formatting from text on a line
	return file_lines[line_no][file_lines[line_no].find('=')+1:].replace("\"","").replace('	',"")


def get_line_key(line_no: int) -> str:
	# Clears away the data from text on a line
	return file_lines[line_no][:file_lines[line_no].find('=')+1].replace("\"","").replace('	',"")


def clean_date(line_no: int) -> str:
	return file_lines[line_no].replace('	',"").replace('{',"").replace('=',"")


def define_bracket_block(start_point: int) -> int:
	# Returns the end point of a bracket ({}) defined block, over one or
	# multiple lines, when given the block's start point.
	bracket_count = 0
	for check_bracket_num in range(start_point,len(file_lines)):
		if '{' in file_lines[check_bracket_num]:
			bracket_count += 1
		if '}' in file_lines[check_bracket_num]:
			bracket_count -= 1
		if bracket_count == 0:
			return check_bracket_num # Returns the line number it ends on
	return -1 # Error, no end


def get_curr_player_countries() -> list:
	global PLAYER_COUNTRIES
	PLAYER_COUNTRIES = []
	start_point = None
	for check_player_countries_num in range(len(file_lines)):
		if file_lines[check_player_countries_num] == "players_countries={":
			start_point = check_player_countries_num
			end_point = define_bracket_block(check_player_countries_num)
			break
	if start_point != None:
		for check_tag_num in range(start_point, end_point):
			if len(get_line_data(check_tag_num)) == 3 and get_line_data(check_tag_num).upper() == get_line_data(check_tag_num):
				PLAYER_COUNTRIES.append(get_line_data(check_tag_num))


def find_colonial_names() -> None:
	global alt_names
	for check_colonial_num in range(len(file_lines)):
		if len(file_lines[check_colonial_num]) == 6:
			if file_lines[check_colonial_num][4:6] == "={":
				if commonfunctions.is_created_nation(file_lines[check_colonial_num][1:4]):
					new_key = get_line_key(check_colonial_num)[:-1]
					start_point = check_colonial_num
					end_point = define_bracket_block(check_colonial_num)
					for check_name_num in range(start_point, end_point):
						if get_line_key(check_name_num) == "name=" and get_line_key(check_name_num+1) == "adjective=":
							new_longname = get_line_data(check_name_num)
							alt_names[new_key] = new_longname
							break				


def locate_wars(filename) -> list:
	global file_lines
	debugfunctions.debug_out(f"Attempting to open [{filename}]")
	try:
		savefile = codecs.open(filename, encoding="latin_1").read()
	except Exception as exception:
		debugfunctions.debug_out(f"Savefile opening failed with exception [{exception}]")
	file_lines = savefile.split("\n")
	if file_lines[0] != "EU4txt": # Compressed save
		short_name = filename.split('/')[-1]
		debugfunctions.debug_out(f"Savefile [{short_name}] is compressed. Decompressing...")
		with zipfile.ZipFile(filename, 'r') as zip:
			zip.extractall()
			savefile = codecs.open("gamestate", encoding="latin_1").read()
			file_lines = savefile.split("\n")
			os.remove("gamestate")
			os.remove("meta")
			os.remove("ai")
		debugfunctions.debug_out("Savefile successfully decompressed.")

	war_list = []
	get_curr_player_countries()
	if len(PLAYER_COUNTRIES) == 0:
		debugfunctions.debug_out("No player countries found",event_type="WARN")
	all_player_nations = ""
	for nat in PLAYER_COUNTRIES:
		all_player_nations += nat+", "
	all_player_nations = all_player_nations[:-2]
	debugfunctions.debug_out(f"Current player nations are {all_player_nations}", event_type="INFO")
	find_colonial_names()
	for i in range(int(len(file_lines)*0.7),len(file_lines)): #!!!!!! (You can set this to like 0.98 for speed loading in testing but it will cut off a lot of early wars)
		if file_lines[i] == "previous_war={":
			start_point = i
			end_point = define_bracket_block(start_point)
			i = end_point+1
			new_war = War(start_point, end_point)
			if new_war.viable == True:
				war_list.append(new_war)
	debugfunctions.debug_out("Finished reading savefile war data")
	debugfunctions.debug_out(f"{str(len(war_list))} viable wars discovered", event_type="INFO")
	if len(war_list) == 0:
		debugfunctions.debug_out("No viable wars discovered!", event_type="ERROR")
	return war_list