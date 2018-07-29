import os
import datetime
import time
import re
import app
from dateutil import tz
from slackclient import SlackClient
from os import environ

slack_client = SlackClient(environ["SLACK_API_TOKEN"])
starterbot_id = None

RTM_READ_DELAY = 1
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"


def convert_time(utc):
    return str(
        utc.replace(tzinfo=tz.gettz('UTC'))
        .astimezone(tz.gettz('Asia/Calcutta'))
        .replace(microsecond=0)
        .replace(tzinfo=None))


def getHelp():
    res = "Hi there, currently the bot supports following commands:\n"
    res += "\n1. upcoming 'sitename': This will give you list of all upcoming\
        contests within a week for the requested site or for all sites if\
        kept blank.\n"
    res += "\n2. ongoing 'sitename': This will give you list of all ongoing\
        contests for the requested site or for all sites if kept blank.\n"
    res += "\n3. help: To get this help message\n"
    return res


def parse_bot_commands(slack_events):
    for event in slack_events:
        if event["type"] == "message" and "subtype" not in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event
    return (None, None)


def parse_direct_mention(message_text):
    matches = re.search(MENTION_REGEX, message_text)
    if (matches):
        return (matches.group(1), matches.group(2).strip())
    else:
        return (None, None)


def handle_command(command, event):
    default_response = "Command not found!"
    response = None

    if command.lower() == "check":
        response = "Check, check done"

    if command.lower().startswith("help"):
        response = getHelp()

    if command.lower().startswith("upcoming"):
        now = datetime.datetime.utcnow()
        if(len(command.split()) > 1):
            response = "Hey <@{0}>, {1}".format(
                event["user"],
                app.upcoming(command.split(' ')[1].lower(), now))
        else:
            response = "Hey <@{0}>, {1}".format(
                event["user"],
                app.upcoming("", now))

    if command.lower().startswith("ongoing"):
        now = datetime.datetime.utcnow()
        if(len(command.split()) > 1):
            response = "Hey <@{0}>, {1}".format(
                event["user"],
                app.ongoing(command.split(' ')[1].lower(), now))
        else:
            response = "Hey <@{0}>, {1}".format(
                event["user"],
                app.ongoing("", now))

    slack_client.api_call(
        "chat.postMessage",
        channel=event["channel"],
        text=response or default_response
    )

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            now = datetime.datetime.utcnow()
            if(now.second == 0):
                ifany, response = app.watchcontest(now)
                if(ifany):
                    slack_client.api_call(
                        "chat.postMessage",
                        channel="CBYGZ19SP",
                        text=response)
            command, event = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, event)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
