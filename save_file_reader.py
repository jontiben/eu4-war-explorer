# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above
# copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

import codecs
import re
import os
import zipfile
import operator
from typing import Tuple, List

import common_functions
import debug_functions
import defines

alt_names = {}  # Dictionary of names for countries created at runtime
nation_info_locations = {}


class Battle:
    def __init__(self, line_loc, name: str, surface: str, date: str, location, result, iteration: int,
                 attacker, attacking_force: list, attacking_losses: int, attacking_general,
                 defender, defending_force: list, defending_losses: int, defending_general,):

        self.name = name
        self.surface = surface  # "land" or "sea"
        self.date = date
        self.location = location  # Province ID
        self.result = result  # "yes" = attacker won, "no" = defender won
        self.iteration = iteration
        self.str_iteration = common_functions.return_ordinal_number(
            str(iteration)) + ' '  # Number of battle (1st, 2nd, 3rd, etc.) fought with the
        # same name in this war, plus a space because I'm lazy
        self.fullname = "NONE"

        self.attacker = attacker  # A tag
        # Below is formatting a list of length 3 (originally cav, art, inf) for land battles,
        # 4 (originally galley, light, heavy, trans) for naval battles
        # Those are transposed to [inf, cav, art] and [heavy, light, galley, trans] respectively
        if len(attacking_force) == 3:
            self.attacking_force = [attacking_force[2], attacking_force[0], attacking_force[1]]
        else:
            self.attacking_force = [attacking_force[2], attacking_force[1], attacking_force[0], attacking_force[3]]
        self.attacking_losses = attacking_losses  # Integer
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
        instances = len([battle for battle in other_battles if battle == self.name])

        if self.iteration == 1 and instances < 2:
            self.str_iteration = ""

        if self.surface == "land":
            self.fullname = self.str_iteration + "Battle of " + self.name
        else:
            words = self.name.split(' ')
            if words[-1] != "Bay" and words[-1] != "Island" and words[0] != "Cape" and words[-1] != "Bank":
                self.fullname = self.str_iteration + "Battle of the " + self.name
            else:
                self.fullname = self.str_iteration + "Battle of " + self.name

    # if self.fullname == "NONE":
    #	debug_functions.debug_out(f"No name found for battle at line {str(line_loc)}", event_type="WARN")


class Participant:
    def __init__(self, war_name, name, side, join_date, quit_date=None, level="secondary", losses=None, warscore=None):
        global alt_names
        self.war_name = war_name

        self.name = name  # Nation's tag
        self.side = side  # "attack" or "defend"
        self.level = level  # "primary" or "secondary"
        self.warscore = warscore
        self.join_date = join_date
        self.quit_date = quit_date
        self.losses = losses

        self.flag_tag = None  # Colonies, used for locating the parent flag with loaded mods

        if self.name[0] == 'C' and common_functions.is_created_nation(self.name):
            colonial_info = self.get_colonial_info()
            self.flag_path = defines.PATH_TO_FLAGS_FOLDER + '/' + colonial_info[0] + ".tga"
            self.flag_tag = colonial_info[0]
            self.country_color = colonial_info[1]
            if self.flag_tag == "":
                self.flag_tag = None
        else:
            self.flag_path = defines.PATH_TO_FLAGS_FOLDER + '/' + self.name + ".tga"
            self.country_color = (150, 150, 150)  # EU4 default

        # Setting up the full name for the nation
        self.longname = None
        if self.name in alt_names.keys():
            if alt_names[self.name] is None:
                self.longname = self.name
            else:
                self.longname = alt_names[self.name]
        elif not common_functions.is_created_nation(self.name):
            self.longname = common_functions.get_full_country_name(self.name)
        else:  # Easier to handle this in here than in common_functions.py because the savefile is already open
            if self.name[0] == 'F':  # Tribal Federation
                if self.level == "primary" and self.side == "attack":
                    self.longname = war_name.split(' ')[1] + ' ' + war_name.split(' ')[2]
                else:
                    self.longname = f"Federation {self.name}"
            if self.longname is None:
                # Last resort
                if "against" in war_name and side == "defend" and level == "primary":
                    self.longname = war_name.split("against ")[-1]
                else:
                    debug_functions.debug_out(
                        f"Couldn't find full name for tag {self.name}. This usually means that it's a colonial nation that's been annexed. Defaulting to tag.",
                        event_type="WARN")
                    self.longname = self.name
                    alt_names[name] = None  # Usually when a colonial nation has been annexed
        if "Federation" in self.longname:
            self.longname = self.longname.replace("The ", '').replace("the ", '')
        self.longname = self.longname[0].upper() + self.longname[1:]
        self.check_dates()

        # In case it doesn't successfully generate a loss list: (I've only ever seen this happen when weird mod
        # mechanics (((Anbennar))) are involved)
        self.inf_losses = 0
        self.cav_losses = 0
        self.art_losses = 0
        self.hs_losses = 0
        self.ls_losses = 0
        self.gal_losses = 0
        self.tra_losses = 0
        self.loss_list = [0, 0, 0, 0, 0, 0, 0]
        self.attrition_losses = 0

    def check_dates(self) -> None:
        # *Occasionally* participants slip through with no self.quit_date, if the war has ended this is probably
        # because they were annexed in a separate peace
        self.quit_date = "annexed"
        # I wonder if there's an easy way to recover the date on which they were annexed?
        # ... I don't think so.

        # Sometimes this happens too?
        if self.join_date == None:
            self.join_date = "unknown"
            debug_functions.debug_out(f"Couldn't find join date for {self.name} in war [{self.war_name}]",
                                      event_type="WARN")

    def consolidate_losses(self) -> None:
        try:
            self.losses = [int(j) for j in self.losses]
        except Exception as exception:
            self.losses = [0 for i in range(defines.CASUALTY_VECTOR_LENGTH)]
            debug_functions.debug_out(
                f"Couldn't find losses for {self.name} in war [{self.war_name}] with exception [{exception}]. Defaulting to zero.",
                event_type="WARN")
        for k in range(2, len(self.losses), 3):
            if self.losses[k] != 0:
                debug_functions.debug_out(
                    f"Nonzero third digit found in losses for {self.name} in war [{self.war_name}]. This is very "
                    f"unusual; please let this utility's creator know if you ever see this and send over the save "
                    f"file. For science.",
                    event_type="INFO")
        # HOW LOSSES WORK: (as far as I can tell)
        # Example: 11403 7835 0 1265 2756 0 8000 5671 0 0 0 0 2 0 0 0 0 0 0 0 0
        # It's broken into groups of three digits. The first three are infantry, second cavalry, third artillery,
        # fourth heavy ships, fifth light ships, sixth galleys, seventh transports. The first number in a group
        # refers to the number lost in combat, the second to attrition, and I'm not sure about the third (I've
        # never seen it anything other than 0). Captured ships count double for the country that lost them in the
        # battle, but don't count at all in final war losses. Losses taken against rebels while fighting in a war
        # get added to the war's total casualties.
        # That same loss line broken up:
        # inf: [11,403; 7,835*; 0] cav: [1,265; 2,756*; 0] art: [8,000; 5,671*; 0] hs: [0; 0*; 0]
        # ls: [2; 0*; 0] gal:[0; 0*; 0] tra:[0; 0*; 0] (attrition has the asterisk)
        loss = self.losses  # Just for convenience
        self.inf_losses = sum(loss[defines.INF_START:defines.INF_END])
        self.cav_losses = sum(loss[defines.CAV_START:defines.CAV_END])
        self.art_losses = sum(loss[defines.ART_START:defines.ART_END])
        self.hs_losses = sum(loss[defines.HS_START:defines.HS_END])
        self.ls_losses = sum(loss[defines.LS_START:defines.LS_END])
        self.gal_losses = sum(loss[defines.GAL_START:defines.GAL_END])
        self.tra_losses = sum(loss[defines.TRA_START:defines.TRA_END])
        self.loss_list = [self.inf_losses, self.cav_losses, self.art_losses, self.hs_losses, self.ls_losses,
                          self.gal_losses, self.tra_losses]
        self.attrition_losses = sum(loss[defines.ATTRITION_OFFSET::defines.GROUP_SIZE])

    def get_colonial_info(self):
        output = ["", [150, 150, 150]]
        if self.name in nation_info_locations.keys():
            for l in range (nation_info_locations[self.name], define_bracket_block(nation_info_locations[self.name])):
                if "colonial_parent" in file_lines[l]:
                    output[0] = file_lines[l].split('=')[1].strip().replace('"', '')
                elif "country_color" in file_lines[l]:
                    colors = clean_tabs(l+1).split(' ')[:3]
                    for c, color in enumerate(colors):
                        output[1][c] = int(color)
        return output  # No colonial parent found


class War:
    def __init__(self, start_point: int, end_point: int):

        self.viable = True  # If there's a problem with the data provided in the save file (e.g. no participants in
        # the Ottoman-Albanian war) this can be set to false and the war won't be included.

        self.start_point = start_point  # First line of the war (should look like "previous_war={ or active_war={")
        self.end_point = end_point  # Line with the war's closing bracket

        # Initializing variables to None so you can easily see what this function is supposed to set
        self.cassus_belli = None
        self.cb_target = None
        self.outcome = None
        # OUTCOMES:
        # 1 - draw
        # 2 - victory for attackers
        # 3 - victory for defenders
        self.start_date = "None"
        self.end_date = "Ongoing"
        self.start_days = 0
        self.attack_total_warscore = 0  # total attacker warscore
        self.defend_total_warscore = 0
        self.has_player = False  # Includes a current player nation
        self.events = []  # List of tuples: (days, date, event)
        self.primary_attacker = "000"
        self.primary_defender = "000"
        self.ongoing = False  # Is the war an "active_war" (True) or a "previous_war" (False)?

        self.battles = []  # All the battles recorded for the war, in chronological order

        self.title = get_line_data(start_point)
        if len(self.title) < 3:
            self.title = get_line_data(start_point+1)
        if self.title == "":
            self.viable = False  # For some reason the game generates 0-length wars with no participants early on
            # in the list of historical wars. These don't have titles.
            debug_functions.debug_out(
                f"Empty war (no title, zero-length) found at line {str(start_point + 1)}. Skipping war.",
                event_type="WARN")
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
        for check_date_num in range(self.history_start + 1, self.history_end):
            if is_date(check_date_num):
                for check_action_num in range(check_date_num + 1, define_bracket_block(check_date_num)):
                    if clean_tabs(check_action_num)[:3] == "add":
                        if "attacker" in clean_tabs(check_action_num):
                            self.attacker_count += 1
                            self.participants[get_line_data(check_action_num)] = Participant(self.title, get_line_data(
                                check_action_num), "attack", clean_date(check_date_num))
                        else:
                            self.defender_count += 1
                            self.participants[get_line_data(check_action_num)] = Participant(self.title, get_line_data(
                                check_action_num), "defend", clean_date(check_date_num))
                    elif clean_tabs(check_action_num)[:3] == "rem":
                        try:
                            self.participants[get_line_data(check_action_num)].quit_date = clean_date(check_date_num)
                        except LookupError:  # Nation is created while the war is going and never gets an entry for joining
                            self.participants[get_line_data(check_action_num)] = Participant(self.title, get_line_data(
                                check_action_num), "attack", None, quit_date=clean_date(check_date_num))

        # Adding other info to participants
        for check_participants_num in range(self.history_end, self.end_point):
            if clean_tabs(check_participants_num)[:12] == "participants":
                curr_tag = get_line_data(check_participants_num + 2)
                self.participants[curr_tag].warscore = float(get_line_data(check_participants_num + 1))
                if self.participants[curr_tag].side == "attack":
                    self.attack_total_warscore += float(get_line_data(check_participants_num + 1))
                else:
                    self.defend_total_warscore += float(get_line_data(check_participants_num + 1))
                self.participants[curr_tag].losses = get_line_data(check_participants_num + 5).split(' ')
                self.participants[curr_tag].consolidate_losses()
        for key in self.participants.keys():
            if self.participants[key].name in PLAYER_COUNTRIES:
                self.has_player = True
                break

        # Miscellaneous war info
        for check_misc_num in range(self.history_end, self.end_point):
            if "cassus_belli" in file_lines[check_misc_num]:
                self.cassus_belli = get_line_data(check_misc_num)
                self.cb_target = get_line_data(check_misc_num - 1)
            if "original_" in file_lines[check_misc_num]:
                try:
                    self.participants[get_line_data(check_misc_num)].level = "primary"
                except LookupError:
                    self.viable = False
                    debug_functions.debug_out(
                        f"Primary participant {get_line_data(check_misc_num)} not in [{self.title}] participants list (bad participant on line {str(check_misc_num)}). Skipping war.",
                        event_type="WARN")
            if "outcome" in file_lines[check_misc_num]:
                self.outcome = get_line_data(check_misc_num)

        if self.viable:
            # Other init functions, split off for readability.
            self.set_primary_participants()
            self.find_battles()
            self.get_total_losses()

        if self.viable:
            original_attacker = None
            for check_original_attacker_num in range(self.history_end, self.end_point):
                if get_line_key(check_original_attacker_num) == "original_attacker=":
                    original_attacker = get_line_data(check_original_attacker_num)
                    break

            if original_attacker is not None:
                self.start_date = self.participants[original_attacker].join_date
                self.start_days = common_functions.date_to_days(self.start_date)
                if self.participants[original_attacker].quit_date != "annexed":
                    self.end_date = self.participants[original_attacker].quit_date
                else:
                    self.ongoing = True
            else:
                debug_functions.debug_out(f"No original attacker found for war [{self.title}]. Skipping war.",
                                          event_type="WARN")

            self.get_events()

    def get_events(self) -> None:
        # Events are tuples formatted (event day #, formatted event date, event name, event type)
        try:
            start_days = common_functions.date_to_days(self.start_date)
            self.events.append((start_days, self.start_date,
                                self.participants[self.primary_attacker].longname + " declared war on " +
                                self.participants[self.primary_defender].longname, "start"))
            if not self.ongoing:
                end_days = common_functions.date_to_days(self.end_date)
                self.events.append((end_days, self.end_date, "War ended", "end"))
            else:
                end_days = common_functions.date_to_days(present_date)
                self.events.append((end_days, present_date, "Present", "end"))

            for participant in self.participants.keys():
                curr_join_days = common_functions.date_to_days(self.participants[participant].join_date)
                curr_quit_days = common_functions.date_to_days(self.participants[participant].quit_date)
                if curr_join_days - start_days > 1:
                    self.events.append((curr_join_days, self.participants[participant].join_date,
                                        self.participants[participant].side + "er " + self.participants[
                                            participant].longname + " joined the war", "join"))
                if curr_quit_days != end_days or self.ongoing:
                    self.events.append((curr_quit_days, self.participants[participant].quit_date,
                                        self.participants[participant].side + "er " + self.participants[
                                            participant].longname + " left the war", "quit"))
            for battle in self.battles:
                self.events.append((common_functions.date_to_days(battle.date), battle.date, battle.fullname, "battle", battle))

            self.events.sort(key=first_element)

        except Exception as exception:
            self.viable = False
            debug_functions.debug_out(
                f"Exception [{exception}] occurred when building event list for [{self.title}]. Skipping war.",
                event_type="WARN")

    def find_battles(self) -> None:
        # Battles are only recorded in the save if they have at least 1,000 total losses (for land battles) or 2
        # ships lost (for naval battles)
        for check_battle_num in range(self.history_start, self.history_end):
            if clean_tabs(check_battle_num) == "battle={" or clean_tabs(check_battle_num) == "battle=":
                battle_date = clean_date(check_battle_num - 1)
                if battle_date == '':
                    battle_date = clean_date(check_battle_num - 2) # Old save compatibility
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
                    elif get_line_key(n) == "location=":
                        battle_location = get_line_data(n)
                    elif get_line_key(n) == "result=":
                        battle_result = get_line_data(n)
                    elif clean_tabs(n) == "attacker={" or clean_tabs(n) == "attacker=":
                        attacker_info = parse_combatant_block(n, define_bracket_block(n))
                    elif clean_tabs(n) == "defender={" or clean_tabs(n) == "defender=":
                        defender_info = parse_combatant_block(n, define_bracket_block(n))
                if len(attacker_info) <= 0:
                    battle_surface = defender_info[0]
                else:  # Just in case a battle only has one combatant saved. It'll still break a few lines down so this
                    # is kind of pointless.
                    battle_surface = attacker_info[0]
                self.battles.append(
                    Battle(check_battle_num, battle_name, battle_surface, battle_date, battle_location, battle_result,
                           curr_iteration,
                           attacker_info[3], attacker_info[1], attacker_info[2], attacker_info[4],
                           defender_info[3], defender_info[1], defender_info[2], defender_info[4]))
        battle_name_list = []
        for battle in self.battles:
            battle_name_list.append(battle.name)
        for battle_obj in self.battles:
            battle_obj.update_name(battle_name_list)

    def set_primary_participants(self):
        for participant in self.participants.keys():
            if self.participants[participant].level == "primary":  # Find the first attacker with the level "primary"
                if self.participants[participant].side == "attack":
                    self.primary_attacker = participant
                elif self.participants[participant].side == "defend":
                    self.primary_defender = participant

    def get_total_losses(self):
        # Does a bunch of arithmetic
        # Also cleans up nations that have had no losses added
        self.attacker_losses = [0 for i in range(defines.CASUALTY_VECTOR_LENGTH)]
        self.defender_losses = [0 for i in range(defines.CASUALTY_VECTOR_LENGTH)]
        for participant in self.participants.keys():
            if self.participants[participant].losses == None:
                self.participants[participant].losses = [0 for i in range(defines.CASUALTY_VECTOR_LENGTH)]
            if self.participants[participant].side == "attack":
                for element in range(len(self.participants[participant].losses)):
                    self.attacker_losses[element] += self.participants[participant].losses[element]
            elif self.participants[participant].side == "defend":
                for element in range(len(self.participants[participant].losses)):
                    self.defender_losses[element] += self.participants[participant].losses[element]

        loss = self.attacker_losses
        self.a_inf_losses = sum(loss[defines.INF_START:defines.INF_END])
        self.a_cav_losses = sum(loss[defines.CAV_START:defines.CAV_END])
        self.a_art_losses = sum(loss[defines.ART_START:defines.ART_END])
        self.a_hs_losses = sum(loss[defines.HS_START:defines.HS_END])
        self.a_ls_losses = sum(loss[defines.LS_START:defines.LS_END])
        self.a_gal_losses = sum(loss[defines.GAL_START:defines.GAL_END])
        self.a_tra_losses = sum(loss[defines.TRA_START:defines.TRA_END])
        self.a_loss_list = [self.a_inf_losses, self.a_cav_losses, self.a_art_losses, self.a_hs_losses, self.a_ls_losses,
                            self.a_gal_losses, self.a_tra_losses]
        self.a_attrition_losses = sum(loss[defines.ATTRITION_OFFSET::defines.GROUP_SIZE])

        loss = self.defender_losses
        self.d_inf_losses = sum(loss[defines.INF_START:defines.INF_END])
        self.d_cav_losses = sum(loss[defines.CAV_START:defines.CAV_END])
        self.d_art_losses = sum(loss[defines.ART_START:defines.ART_END])
        self.d_hs_losses = sum(loss[defines.HS_START:defines.HS_END])
        self.d_ls_losses = sum(loss[defines.LS_START:defines.LS_END])
        self.d_gal_losses = sum(loss[defines.GAL_START:defines.GAL_END])
        self.d_tra_losses = sum(loss[defines.TRA_START:defines.TRA_END])
        self.d_loss_list = [self.d_inf_losses, self.d_cav_losses, self.d_art_losses, self.d_hs_losses, self.d_ls_losses,
                            self.d_gal_losses, self.d_tra_losses]
        self.d_attrition_losses = sum(loss[defines.ATTRITION_OFFSET::defines.GROUP_SIZE])


def parse_combatant_block(start_point: int, end_point: int) -> list:
    # Returns a list:
    # [surface, [force], losses, tag, general name]
    ground_forces = {"cavalry": 0, "artillery": 0, "infantry": 0}
    sea_forces = {"galley": 0, "light_ship": 0, "heavy_ship": 0, "transport": 0}
    # Dictionaries allow you to make the combatants always stick to the same order in the list output on the other side.
    out_list = []
    for o in range(start_point, end_point):
        current_keyword = get_line_key(o).replace('=', "")
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


def check_mods(mod_list) -> str | None:
    global alt_names
    modded_map_path = None
    for mod in mod_list:
        mod_path = mod[0].split('/')[1]
        debug_functions.debug_out(f"Found mod {mod[1]}")
        current_mod_file = open(f"{defines.EU4_MODS}/{mod_path}", 'r')
        current_mod_lines = current_mod_file.readlines()
        current_mod_file.close()
        mod_data_path = None
        for line in current_mod_lines:
            if line[:5] == "path=":
                mod_data_path = line[6:-2]
        if mod_data_path is None:
            debug_functions.debug_out(f"Failed to find path for mod {mod[1]}", event_type="WARN")
            return
        if os.path.isdir(mod_data_path+"/common/country_tags/"):
            tag_names = common_functions.get_all_country_names(countries_folder=mod_data_path+"/common/country_tags/")
            for tag in tag_names:
                alt_names[tag[0]] = tag[1]
        if os.path.isdir(mod_data_path+"/gfx/flags"):
            common_functions.load_modded_flags(mod_data_path)
        if os.path.isfile(mod_data_path+"/map/terrain.bmp"):
            modded_map_path = mod_data_path+"/map"
    return modded_map_path


# The following are mostly utility functions.
def first_element(input_list: list):
    return input_list[0]


def is_date(line_no: int) -> bool:
    # Determines if the data in a given line is a properly-formatted date
    line = clean_date(line_no)
    if re.fullmatch(r"\d{4}.\d\d?.\d\d?", line) != None:
        return True
    return False


def clean_tabs(line_no: int) -> str:
    return file_lines[line_no].replace('	', "")


def get_line_data(line_no: int) -> str:
    # Clears away formatting from text on a line
    return file_lines[line_no][file_lines[line_no].find('=') + 1:].replace("\"", "").replace('	', "")


def get_line_key(line_no: int) -> str:
    # Clears away the data from text on a line
    return file_lines[line_no][:file_lines[line_no].find('=') + 1].replace("\"", "").replace('	', "")


def clean_date(line_no: int) -> str:
    return file_lines[line_no].replace('	', "").replace('{', "").replace('=', "")


def define_bracket_block(start_point: int) -> int:
    # Returns the end point of a bracket ({}) defined block, over one or
    # multiple lines, when given the block's start point.
    bracket_count = 0
    for check_bracket_num in range(start_point, len(file_lines)):
        if '{' in file_lines[check_bracket_num]:
            bracket_count += 1
        if '}' in file_lines[check_bracket_num]:
            bracket_count -= 1
        if bracket_count == 0 and check_bracket_num > start_point:
            return check_bracket_num  # Returns the line number it ends on
    return -1  # Error, no end


def get_curr_player_countries() -> None:
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
            if len(get_line_data(check_tag_num)) == 3 and get_line_data(check_tag_num).upper() == get_line_data(
                    check_tag_num):
                PLAYER_COUNTRIES.append(get_line_data(check_tag_num))


# Gets the present date (formatted like "date=XXXX.XX.XX")
def get_present_date() -> str:
    return get_line_data(1)


def find_colonial_names() -> None:
    global alt_names
    for check_colonial_num in range(len(file_lines)):
        if len(file_lines[check_colonial_num]) == 5:
            if file_lines[check_colonial_num][3:5] == "={":
                if common_functions.is_created_nation(file_lines[check_colonial_num][:3]):
                    new_key = get_line_key(check_colonial_num)[:-1]
                    start_point = check_colonial_num
                    end_point = define_bracket_block(check_colonial_num)
                    for check_name_num in range(start_point, end_point):
                        if get_line_key(check_name_num) == "name=" and get_line_key(check_name_num + 1) == "adjective=":
                            new_longname = get_line_data(check_name_num)
                            alt_names[new_key] = new_longname
                            break


def get_meta_data(local_file_lines) -> list:
    meta_data_out = ["", [], ""]  # Checksum, Mod locations, Game version,
    for l, line in enumerate(local_file_lines):
        if line == "savegame_version=":
            meta_data_out[2] = f"{get_line_data(l + 2)}.{get_line_data(l + 3)}.{get_line_data(l + 4)}"
        elif line == "savegame_version={":
            meta_data_out[2] = f"{get_line_data(l + 1)}.{get_line_data(l + 2)}.{get_line_data(l + 3)}"
        elif line == "mods_enabled_names={":
            for i in range(l, define_bracket_block(l)):
                if clean_tabs(i) == "{":
                    path = get_line_data(i+1)
                    if os.path.isfile(defines.EU4_MODS + '/' + path.split('/')[1]):
                        meta_data_out[1].append((get_line_data(i+1), get_line_data(i+2)))
                    else:
                        debug_functions.debug_out(f"Failed to find .mod file at path [{defines.EU4_MODS + '/' + path.split('/')[1]}]", event_type="WARN")
                    break
        elif line == "mod_enabled={":  # I think mod_enabled is the old name for this
            for i in range(l+1, define_bracket_block(l)):
                if clean_tabs(i) != "}":
                    path = clean_tabs(i).replace('\"', "")
                    if os.path.isfile(defines.EU4_MODS + '/' + path.split('/')[1]):
                        meta_data_out[1].append((path, path.split('_')[1][:-4]))
                    else:
                        debug_functions.debug_out(f"Failed to find .mod file at path [{defines.EU4_MODS + '/' + path.split('/')[1]}]", event_type="WARN")
                    break
        elif "checksum=" in line:
            # End of meta file/section
            meta_data_out[0] = get_line_data(l)
            break
    return meta_data_out


def locate_wars(filename) -> tuple[list[War], str, str] | None:
    global file_lines, present_date, nation_info_locations
    debug_functions.debug_out(f"Attempting to open [{filename}]")
    try:
        savefile = codecs.open(filename, encoding="latin_1").read()
    except Exception as exception:
        debug_functions.debug_out(f"Savefile opening failed with exception [{exception}]")
        return None
    file_lines = savefile.split("\n")
    meta_savefile, meta_file_lines = None, None
    if file_lines[0].strip() != "EU4txt":  # Compressed save
        short_name = filename.split('/')[-1]
        debug_functions.debug_out(f"Savefile [{short_name}] is compressed. Decompressing...")
        with zipfile.ZipFile(filename, 'r') as zip:
            zip.extractall()
            savefile = codecs.open("gamestate", encoding="latin_1").read()
            file_lines = savefile.split("\n")
            meta_savefile = codecs.open("meta", encoding="latin_1").read()
            meta_file_lines = meta_savefile.split("\n")
            os.remove("gamestate")
            os.remove("meta")
            os.remove("ai")
            try:
                os.remove("rnw.zip")  # Handling random new worlds
            except:
                pass
        debug_functions.debug_out("Savefile successfully decompressed.")

    present_date = get_present_date()
    for l in range(len(file_lines)): # Necessary for compabtibility with older saves
        file_lines[l] = file_lines[l].strip()
    war_list = []
    get_curr_player_countries()
    if len(PLAYER_COUNTRIES) == 0:
        debug_functions.debug_out("No player countries found", event_type="WARN")
    all_player_nations = ""
    for nat in PLAYER_COUNTRIES:
        all_player_nations += nat + ", "
    all_player_nations = all_player_nations[:-2]
    debug_functions.debug_out(f"Current player nations are {all_player_nations}", event_type="INFO")
    if meta_savefile is None:
        meta_data = get_meta_data(file_lines)
    else:
        file_lines = meta_file_lines + file_lines
        meta_data = get_meta_data(meta_file_lines)
    find_colonial_names()
    checksum = meta_data[0]
    map_mod_location = check_mods(meta_data[1])
    game_version = meta_data[2]
    for i in range(len(file_lines)):
        if len(file_lines[i]) == 5:
            if file_lines[i][:1] == "C":
                if file_lines[i][3:5] == "={":
                    if "has_set_government_name" in file_lines[i+1] or "pillaged_capital_state" in file_lines[i+1]:  # Edge case? Maybe others?
                        nation_info_locations[file_lines[i][0:3]] = i
        elif i > int(len(file_lines) * 0.7):  # !!!!!! (You can set this to like 0.98 for speed
        # loading in testing, but it will cut off a lot of early wars)
            check_file_line = file_lines[i].strip()
            if check_file_line == "previous_war={" or check_file_line == "active_war={" or check_file_line == "previous_war=" or check_file_line == "active_war=":
                # non-bracket variants are found in old saves
                start_point = i
                if '{' not in file_lines[i]:
                    start_point += 1
                end_point = define_bracket_block(start_point)
                i = end_point + 1
                new_war = War(start_point, end_point)
                if new_war.viable:
                    war_list.append(new_war)
    war_list = sorted(war_list, key=operator.attrgetter("start_days"))
    debug_functions.debug_out("Finished reading savefile war data")
    debug_functions.debug_out(f"{str(len(war_list))} viable wars discovered", event_type="INFO")
    if len(war_list) == 0:
        debug_functions.debug_out("No viable wars discovered! (something's wrong)", event_type="ERROR")
    return (war_list, present_date, map_mod_location, checksum, game_version)
