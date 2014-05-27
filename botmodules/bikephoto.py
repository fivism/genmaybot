import re
import sqlite3
import urllib.request
from urllib.parse import urlparse

#Handles !bike, !bikephoto, and !photo

def __init__(self):
	
	conn = sqlite3.connect('bikephoto.sqlite')
	c = conn.cursor()
	result = c.execute("CREATE TABLE IF NOT EXISTS bikePhoto (nick TEXT, bikephoto TEXT, photo TEXT, bike TEXT)")
	conn.commit()
	c.close()

# --- Commands in this module

def bikephoto(self, event):
	command_handler(self, event, "bikephoto")
	return event

bikephoto.command = "!bikephoto"
bikephoto.helptext = "bikephoto help text"

def photo(self, event):
	command_handler(self, event, "photo")
	return event

photo.command = "!photo"
photo.helptext = "photo help text"

def bike(self, event):
	command_handler(self, event, "bike")
	return event

bike.command = "!bike"
bike.helptext = "bike help text"

# --- End commands

def command_handler(self, event, command):

	nick_offset = 0
	command_offset = 0
	arg_offset = 1
	nick = event.nick

	#split the user input along word boundary into list
	words = event.input.split()
	word_len = len(words)


	#event.input omits the "!command", so we just need to check and make sure we got at least one
	if(word_len):
		#Two commands, set and get. get is implicit when set is not present and is not explicitly sent by the user

		#SET - Make sure we have another word after the command
		if(word_len >= 2 and words[command_offset] == "set"):
			# Handle all photo commands generically as URL storing
			if(command == "bikephoto" or command == "photo"):
				# Support multiple urls, get all the args
				store_url_for_nick(nick, words[arg_offset:], command, event)
			# Handle anything thats not a URL as generic string storing
			if(command == "bike"):
				store_string_for_nick(nick, words[arg_offset:], command, event)
		
		#SET with no parameters, print some help text
		elif(word_len and words[command_offset] == "set"):
			event.output = "You didnt specify a " + command

		#GET with an arg- 
		else:
			event.output = "Looking up  " + command + " for: " + words[nick_offset]
			get_string_for_nick(words[nick_offset], command, event)

	#GET on self
	else:
		event.output = "Looking up your " + command + ", " + nick
		get_string_for_nick(nick, command, event)


	return event

def store_url_for_nick(nick, words, command, event):

	url_string = ""
	space = " "

	for word in words:
		try:
			urllib.request.urlopen(word, None, 3)
		except urllib.error.URLError:
			event.output += "URL: " + word + " is unreachable\n"
			continue
		except:
			event.output += "URL: " + word + " is invalid.\n"
			continue

		print("DEBUG: adding " + word)
		url_string += word
		url_string += space

	store_string_for_nick(nick, url_string, command, event)
	return

def store_string_for_nick(nick, words, command, event):

	string = ""
	space = " "
	
	#Stringify lists, dont mess with strings
	if not isinstance(words, str):
		for word in words:
			string += word
			string += space
			print("DEBUG: adding " + word)
	else:
		string = words

	event.output += "\nStoring " + command + ": " + string + "for " + nick

	sql_insert_or_update(nick, command, string)
	
	return

def get_string_for_nick(nick, command, event):

	#Didnt find one
	string = sql_get_value_from_command(nick, command)
	if string == None:
		print("didnt find one")

	#Found one
	else:
		event.output += "\n" + command + ": " + string
	
	return

def sql_insert_or_update(nick, command, string):

	conn = sqlite3.connect('bikephoto.sqlite')
	c = conn.cursor()

	#New user
	result = c.execute("SELECT nick FROM bikePhoto WHERE nick=?", (nick,)).fetchone() 
	if result == None:
		print("DEBUG: New nick, inserting " + command + " value: " + string)

		query = "INSERT INTO bikePhoto (nick,%s) VALUES (?,?)" % command
		result = c.execute(query, (nick, string,))
		if not result:
			print("DEBUG: Failed to insert value")

	#Existing user
	else:
		print("DEBUG: Existing nick, inserting " + command + " value: " + string)
		query = "UPDATE bikePhoto set %s = ? WHERE nick=?" % command
		result = c.execute(query, (string, nick,))
		if not result:
			print("DEBUG: Failed to update value")

	conn.commit()

	print("Current db state: ")
	for row in c.execute("SELECT * FROM bikePhoto"):
		print(row)

	c.close()
	return

def sql_get_value_from_command(nick, command):

	conn = sqlite3.connect('bikephoto.sqlite')
	c = conn.cursor()

	query = "SELECT %s FROM bikePhoto WHERE nick=?" % command
	value = c.execute(query, (nick,)).fetchone()
	c.close()
	
	if value == None:
		return;
	
	return value[0]

