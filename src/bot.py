# -*- coding: utf-8 -*-
"""
Python Slack Bot class for use with the pythOnBoarding app
"""
import os
import message

from slackclient import SlackClient

authed_teams = {}


class Bot(object):
    def __init__(self):
        super(Bot, self).__init__()
        self.name = "vertuhai"
        self.emoji = ":robot_face:"
        self.oauth = {"client_id": os.environ.get("CLIENT_ID"),
                      "client_secret": os.environ.get("CLIENT_SECRET"),
                      "scope": "bot"}
        self.verification = os.environ.get("VERIFICATION_TOKEN")

        slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
        self.client = SlackClient(slack_bot_token)
        # self.client = SlackClient("")
        self.messages = {}

    def auth(self, code):
        auth_response = self.client.api_call(
                                "oauth.access",
                                client_id=self.oauth["client_id"],
                                client_secret=self.oauth["client_secret"],
                                code=code
                                )
        team_id = auth_response["team_id"]
        authed_teams[team_id] = {"bot_token":
                                 auth_response["bot"]["bot_access_token"]}

        self.client = SlackClient(authed_teams[team_id]["bot_token"])

    def direct_message(self, message, channel):
        post_message = self.client.api_call("chat.postMessage", channel=channel, text=message)
        print post_message
        # timestamp = post_message["ts"]
        # message_obj.timestamp = timestamp
