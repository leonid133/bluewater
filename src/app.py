# -*- coding: utf-8 -*-
"""
A routing layer for the onboarding bot tutorial built using
[Slack's Events API](https://api.slack.com/events-api) in Python
"""
import json
import bot
from queue import DummyToiletQueue
from flask import Flask, request, make_response, render_template
import requests

pyBot = bot.Bot()
slack = pyBot.client
queue = DummyToiletQueue()

app = Flask(__name__)


def book(user_id, channel):
    message = "<@%s> You booked! :tada:" % user_id
    pyBot.direct_message(message, channel)


def check_status(user_id, channel):
    message = "<@%s> You will be get status! :tada:" % user_id
    pyBot.direct_message(message, channel)


def go_to_hell(user_id, channel):
    message = "<@%s> Fuck You! :tada:" % user_id
    pyBot.direct_message(message, channel)


def omg(user_id, channel):
    message = "<@%s> OMG! :tada:" % user_id
    pyBot.direct_message(message, channel)


def other(user_id, channel):
    message = "<@%s> other! :tada:" % user_id
    pyBot.direct_message(message, channel)


def _event_handler(event_type, slack_event):
    team_id = slack_event["team_id"]
    user_id = slack_event["event"].get("user")

    if event_type == "message" and user_id is not None:
        print slack_event
        token = slack_event["token"]

        channel = slack_event["event"].get("channel")

        # curl - X
        # POST - -header
        # 'Content-Type: application/json' - -header
        # 'Accept: application/json' - d
        # '{ "msg": [ "foo" ] }' 'https://dev.k8s.hydrosphere.io/gateway/applications/bluewater-nlp/bluewater-nlp'
        in_message = {
            "msg": [slack_event.get("event", {}).get("text", "")]
        }
        messag_from_user = json.dumps(in_message, indent=2)
        print messag_from_user
        ml_request = requests.post(pyBot.nlp_http, data=messag_from_user)

        intent_labels = {
            'Book': book,
            'CheckStatus': check_status,
            'GoToHell': go_to_hell,
            'OMG': omg,
            'Other': other
        }

        dialect = intent_labels.get(ml_request.get("INTENT_LABELS"))

        dialect(user_id, channel)

        # msg = "Hello <@%s>! I'll call you!" % user_id
        # pyBot.direct_message(msg, channel)

        who_whanna_go = {
            'token': token,
            'team_id': team_id,
            'user_id': user_id,
            'channel': channel
        }
        print json.dumps(who_whanna_go, indent=2)
        return make_response("!!!!",
                             200, )
    message = "You have not added an event handler for the %s" % event_type
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/welcome", methods=["POST"])
def welcome():
    return make_response("Hey-hey!")


@app.route("/health", methods=["GET"])
def health():
    return make_response("I'm healthy", 200)


@app.route("/install", methods=["GET", "POST"])
def pre_install():
    client_id = pyBot.oauth["client_id"]
    scope = pyBot.oauth["scope"]
    return render_template("install.html", client_id=client_id, scope=scope)


@app.route("/thanks", methods=["GET", "POST"])
def thanks():
    code_arg = request.args.get('code')
    pyBot.auth(code_arg)
    return render_template("thanks.html")


@app.route("/sensor", methods=["POST"])
def sensor():
    # print request.__dict__
    try:
        data = json.loads(request.data)
        print data
        status = data.get('status', 0)
        print status
        if status is 0:
            queue.remove()
    except:
        print 'error'
    return make_response("Ok.", 200, )


@app.route("/timetogo", methods=["GET", "POST"])
def timetogo():

    print request.__dict__
    try:
        queue_event = json.loads(request.data)
        user_id = queue_event.get('user_id', "")
        channel = queue_event.get('channel', "")
    except:
        # team_id = request.args.get('team_id')
        user_id = request.args.get('user_id')
        channel = request.args.get('channel')

    message = "Time to go <@%s>! :tada:" % user_id
    pyBot.direct_message(message, channel)
    return make_response("Ok.",
                         200, )


@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    print slack_event

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                                 "application/json"
                                                             })

    if pyBot.verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s \npyBot has: \
                   %s\n\n" % (slack_event["token"], pyBot.verification)
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


if __name__ == '__main__':
    app.run(debug=True)
