import os
import time
import re
from slackclient import SlackClient
import requests
import json
from pyngrok import ngrok
import datetime
#import mysql.connector
import logging
logging.basicConfig()

#DBA Connection
#mydb = mysql.connector.connect(
#	host="localhost",
#	user="root",
#	password="passw+++ord")


# instantiate Slack client with OAUTH
slack_client = SlackClient('xoxb-1474844397573-1502414790320-NCyqg5kK4hUFH45n1JsLvKen')
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None
#Ngrok http tunnel
http_tunnel = ngrok.connect()


# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
INFO_COMMAND = "info"
SEARCH_COMMAND = "search"
CHANGE_COMMAND = "change"
HELP_COMMAND = "help"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
url = None

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(HELP_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # Info command
    if command.startswith(INFO_COMMAND):
        
        #JSON Request to middleware
        request = {
        "id": "EUApp_RAT_Bot",
        "url": http_tunnel,
        "date": datetime.datetime.now().isoformat()
        }  

        #Format message from Slack Client
        convertedCommand = command.encode()
        convertedCommand = convertedCommand.replace("<", "")
        convertedCommand = convertedCommand.replace(">", "")
        destino1 = convertedCommand.split()
        #IP of Middleware fon info
        destino = destino1[1] + "info/"
       
       
       	#Tranformar el request como JSON
       	requestJson = json.dumps(request)
       	print("Request: "+requestJson)
       	#Mandar JSON al Middleware, retorna JSON
        respuesta = requests.post(destino, data=requestJson)
        #Mandar al Cliente de slack
        response = respuesta.text
        print(response)
    #Comando para search
    if command.startswith(SEARCH_COMMAND):
    	convertedCommand = command.encode()
    	convertedCommand = convertedCommand.replace("<", "")
    	convertedCommand = convertedCommand.replace(">", "")
    	convertedCommand = convertedCommand.split()
    	destino1 = convertedCommand[1]
    	idHardware = convertedCommand[2]
    	startDate = convertedCommand[3]
    	finishDate = convertedCommand[4]
    	destino = destino1 + "search/"

    	startDate = startDate + "T00:00:00.000Z"
    	finishDate = finishDate + "T00:00:00.000Z"

    	request = {
			"id": "EUApp_RAT_Bot",
        	"url": http_tunnel,
        	"date": datetime.datetime.now().isoformat(),
        	"search": {
        	"id_hardware": idHardware,
        	"start_date": startDate,
        	"finish_date": finishDate
        	}}
        requestJson = json.dumps(request)
        print("Request: "+requestJson)
        respuesta = requests.post(destino, data=requestJson)
        response = respuesta.text
        print(response)
    if command.startswith(CHANGE_COMMAND):
		convertedCommand = command.encode()
		convertedCommand = convertedCommand.replace("<", "")
		convertedCommand = convertedCommand.replace(">", "")
		convertedCommand = convertedCommand.split()
		destino1 = convertedCommand[1]
		idHardware = convertedCommand[2]
		status = convertedCommand[3]
		texto = convertedCommand[4]
		destino = destino1 + "change/"

		request = {
			"id": "EUApp_RAT_Bot",
			"url": http_tunnel,
			"date": datetime.datetime.now().isoformat(),
			"change": {
			idHardware : {
				"status": status,
				"text": texto
			}}}
		requestJson = json.dumps(request)
		print("Request: "+requestJson)
		respuesta = requests.post(destino, data=requestJson)
		response = respuesta.text
		print(response)
		if command.startswith(HELP_COMMAND):
			response = "Puede utilizar el comando info"

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("RAT Bot for Slack connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                print(command)
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
