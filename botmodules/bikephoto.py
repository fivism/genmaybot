import re
import sqlite3
import urllib.request
import urllib.parse

#Handles !bike, !bikephoto, and !photo

#TODO - dont split url failure output

g_irc_output = ""

def __init__(self):
	
	conn = sqlite3.connect('bikephoto.sqlite')
	c = conn.cursor()
	result = c.execute("CREATE TABLE IF NOT EXISTS bikePhoto (nick TEXT, bikephoto TEXT, photo TEXT, bike TEXT)")
	conn.commit()
	c.close()

# --- Commands in this module

def bikephoto(self, event):
	command_handler(event, "bikephoto")
	return event

bikephoto.command = "!bikephoto"
bikephoto.helptext = "Use \"" + bikephoto.command + " [nick]\" for look up, and \"" + bikephoto.command + " set <valid URL>\" to create a new one"


def photo(self, event):
	command_handler(event, "photo")
	return event

photo.command = "!photo"
photo.helptext = "Use \"" + photo.command + " [nick]\" for look up, and \"" + photo.command + " set <valid URL>\" to create a new one"

def bike(self, event):
	command_handler(event, "bike")
	return event

bike.command = "!bike"
bike.helptext = "Use \"" + bike.command + " [nick]\" for look up, and \"" + bike.command + " set <string>\" to create a new one"

# --- End commands

def command_handler(event, command):
	
	nick_offset = 0
	arg_offset = 0
	val_offset = 1

	nick = event.nick
	irc_input = event.input

	set_function_dict = {'bikephoto':store_url_for_nick, 'photo':store_url_for_nick, 'bike':store_string_for_nick}
	get_function_dict = {'bikephoto':get_string_for_nick, 'photo':get_string_for_nick, 'bike':get_string_for_nick}

	#split the user input along word (whitespace) boundary into list 
	#EX: "set http://url1 http://url2 http://url3"
	words = irc_input.split()

	if(arg_is_present(words)):

		# SET <VAL>
		# "set http://valid.url.here"
		if(is_set_arg(words, arg_offset)):
			set_function_dict[command](nick, words[val_offset:], command)

		# SET
		# EX: "set"
		elif(is_arg_without_val(words, arg_offset)):
			# This eval should be safe, possible values of command are hard coded above.
			add_to_irc_output(eval(command).helptext)

		# GET <VAL>
		# EX: "lance_armstrong"
		else:
			get_function_dict[command](words[nick_offset], command)

	# GET
	# EX: ""
	else:
		get_function_dict[command](nick, command)

	flush_and_reset_irc_output(event)

	return event

def arg_is_present(words):
	return len(words)

def is_set_arg(words, offset):
	return(len(words) >= 2 and words[offset] == "set")

def is_arg_without_val(words, offset):
	return(len(words) == 1 and words[offset] == "set")

def store_url_for_nick(nick, urls, command):
	url_string = ""
	space = " "

	for url in urls:
		try:
			urllib.request.urlopen(url, None, 1)
		except urllib.error.URLError:
			add_to_irc_output("URL: " + url + " is unreachable. ")
			continue
		except:
			add_to_irc_output("URL: " + url + " is invalid. ")
			continue

		url_string += url
		url_string += space

	#We have at least 1 valid URL
	if not url_string == "":
		store_string_for_nick(nick, url_string, command)

	return 1

def store_string_for_nick(nick, words, command):
	string = ""
	space = " "
	
	#Stringify lists, dont mess with strings
	if not isinstance(words, str):
		for word in words:
			string += word
			string += space
			#print("DEBUG: adding " + word)
	else:
		string = words

	add_to_irc_output("\nStoring " + command + " " + string + "for " + nick)

	sql_insert_or_update(nick, command, string)
	
	return 1

def get_string_for_nick(nick, command):

	#Didnt find one
	string = sql_get_value_from_command(nick, command)
	if string == None:
		add_to_irc_output("\n" + command + " not found for " + nick)

	#Found one
	else:
		add_to_irc_output("\n" + command + ": " + string)
	
	return 1

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
	return 1

def sql_get_value_from_command(nick, command):

	conn = sqlite3.connect('bikephoto.sqlite')
	c = conn.cursor()

	query = "SELECT %s FROM bikePhoto WHERE nick=?" % command
	value = c.execute(query, (nick,)).fetchone()
	c.close()
	
	if value == None:
		return 0;
	
	return value[0]

def add_to_irc_output(output):
	global g_irc_output
	g_irc_output += output

def flush_and_reset_irc_output(event):
	global g_irc_output
	
	event.output = g_irc_output
	g_irc_output = ""


# Offline debugging

class debug_event:
	output = ""
	input = ""
	nick = "debug_nick"

def debug():
	self = ""
	event = debug_event()
	__init__(self)

	print("Command:")
	command = input()
	print ("Args:")
	args = input()
	event.input = args

	#import pdb; pdb.set_trace()
	for word in command.split():
		if word == "!bikephoto":
			bikephoto(self, event)
		if word == "!bike":
			bike(self, event)
		if word == "!photo":
			photo(self, event)

	print("All done, output is: " + event.output)

#debug()
