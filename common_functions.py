#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

import re
import os
import defines
import pygame
import debugfunctions

def return_ordinal_number(number: str) -> str:
	# Converts a number to its ordinal form
	ordinal_dict = {'1': "st", '2': "nd", '3': "rd"}
	if number == "11" or number == "12" or number == "13":
		return number+"th"
	if number[-1] in ordinal_dict.keys():
		return number+ordinal_dict[number[-1]]
	return number+"th"

def break_up_large_numbers(number: str) -> str:
	number = str(number)
	# Adds a comma every three digits
	new_text = ""
	for i in range(len(number)):
		new_text += number[i]
		if (len(number)-(i+1)) % 3 == 0 and i != len(number)-1:
			new_text += ","
	return new_text

def is_created_nation(tag: str) -> bool:
	# Returns True if the tag is dynamically generated (client state (K), colonial nation (C),
	# trade city (T), federation (F), or custom nation (D)). False if it is anything else.
	if re.fullmatch(r"(C|D|F|K|T)\d\d",tag) != None:
		return True
	return False

def get_full_country_name(tag: str) -> str:
	# Takes a three-character tag and returns the full name
	# Case-insensitive
	# KER (Zia) has an incorrect number of spaces in its filename which is why I have to use .split('-')
	for files in os.walk(defines.PATH_TO_COUNTRIES_FOLDER):
		for filename in files[-1]:
			if filename[:3] == tag.upper():
				name = filename[:-4].split('-')[1]
				if name[0] == ' ':
					return name[1:]
				return name
	return tag

def date_conversion(date: str) -> str:
	# Takes a normally-formatted date string and turns it into
	# DD Month YYYY
	if date == "annexed" or date == "unknown":
		return date
	month_list = ["January", "February", "March", "April", "May", "June", "July", "August",
	"September", "October", "November", "December"]
	date = date.split('.')
	year = date[0]
	month = month_list[int(date[1])-1]
	day = date[2]
	return day+" "+month+" "+year

def lookup_outcome(code) -> str:
	# Returns a description of the war's outcome when given the outcome code
	# OUTCOMES:
	# 1 - draw
	# 2 - victory for attackers
	# 3 - victory for defenders
	if code != None:
		outcome_list = ["White Peace","Attacker Won","Defender Won"]
		return outcome_list[int(code)-1]
	return "Outcome Unknown"

def date_to_days(date: str) -> int:
	if type(date) == type(None):
		return 0
	elif date == "annexed" or date == "unknown":
		return 0
	# Takes in a date (string) formatted like XXXX.XX.XX and converts it to an integer representing the number of days since January 1, AD 1
	try:
		months = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30] # January-November, don't need to add December because it's the last month
		date = date.split('.')
		year, month, day = int(date[0]), int(date[1]), int(date[2])
		return (year-1)*365 + sum(months[:month]) + day - 1
	except:
		return 0
	return 0

def load_flag(tag: str, war):
	try:
		flag = pygame.image.load(war.participants[tag].flag_path)
	except:
		flag = pygame.image.load(defines.PATH_TO_BACKUP_FLAG)
		debugfunctions.debug_out(f"Failed to open flag for tag {tag}",event_type="WARN")
	return flag
