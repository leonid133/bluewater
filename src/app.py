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
import sys

pyBot = bot.Bot()
slack = pyBot.client
queue = DummyToiletQueue()
last_state = 0
last_id = 0
free_count = 0
busy_count = 0
last_free_count = 0
last_busy_count = 0

app = Flask(__name__)


def book(user_id, channel):
    global queue
    if channel in queue.get():
        message = "<@%s> You are pidor and you are already in the queue!" % user_id
    else:
        queue.add(channel)
        st = queue.get_my_status(channel)
        message = "<@%s> You booked! You're the %d's in the queue :tada:" % (user_id, st)
    pyBot.direct_message(message, channel)


def check_status(user_id, channel):
    global queue
    st = queue.get_my_status(channel)
    if st != -1:
        message = "<@%s> You're the %s in the queue :tada:" % (user_id, st)
    else:
        message = "<@%s> You're not in the queue (because you are pidor)" % user_id
    pyBot.direct_message(message, channel)


def go_to_hell(user_id, channel):
    message = "<@%s> Fuck You! Nu ty i pidor! :tada:" % user_id
    pyBot.direct_message(message, channel)


def omg(user_id, channel):
    message = "<@%s> OMG! :tada:" % user_id
    pyBot.direct_message(message, channel)


def other(user_id, channel):
    message = "<@%s> Nu ya hui znaet :tada:" % user_id
    pyBot.direct_message(message, channel)


def _event_handler(event_type, slack_event):
    team_id = slack_event["team_id"]
    user_id = slack_event["event"].get("user")

    if event_type == "message" and user_id is not None:
        token = slack_event["token"]
        channel = slack_event["event"].get("channel")
        in_message = {
            "msg": [slack_event.get("event", {}).get("text", "")]
        }
        ml_request = requests.post(pyBot.nlp_http, json=in_message)

        intent_labels = {
            'Book': book,
            'CheckStatus': check_status,
            'GoToHell': go_to_hell,
            'OMG': omg,
            'Other': other
        }
        dialect = intent_labels.get(ml_request.json().get("intent")[0])
        dialect(user_id, channel)

        who_whanna_go = {
            'token': token,
            'team_id': team_id,
            'user_id': user_id,
            'channel': channel
        }
        print json.dumps(who_whanna_go, indent=2)

        return make_response("!!!!", 200, )
    message = "You have not added an event handler for the %s" % event_type
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/queue", methods=["GET"])
def get_queue():
    return make_response(json.dumps(queue.get()), 200, {'Content-Type': 'application/json'})


@app.route("/welcome", methods=["POST"])
def welcome():
    global last_id
    last_id = 0
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
    global last_state
    global last_id
    global queue
    global free_count
    global busy_count
    global last_free_count
    global last_busy_count
    try:
        data = json.loads(request.data)
        status = data.get('status', 0)
        ident = data.get('id', 0)
        if ((busy_count > 3600) or (free_count > 120) or (status is 1 and last_state is 0)) and last_id < ident:
            print "removing from queue because (last_id=%d && id=%d), (last_state=%d && status=%d)" % (last_id, ident, last_state, status)
            last_id = ident
            channel = queue.remove()
            message = "go go go"
            pyBot.direct_message(message, channel)
            last_free_count = free_count
            last_busy_count = busy_count
            free_count = 0
            busy_count = 0
            last_state = status
        elif status is 1 and last_state is 1 and last_id < ident:
            free_count = free_count + 1
            last_state = status
        elif status is 0 and last_state is 0 and last_id < ident:
            busy_count = busy_count + 1
            last_state = status
        elif last_id < ident:
            last_state = status

    except Exception as e:
        print 'error', sys.exc_info()[0]
        raise e
    return make_response("Ok.", 200, )


@app.route("/get_info", methods=["GET"])
def get_info():
    global last_state
    global last_id
    global free_count
    global busy_count
    global last_free_count
    global last_busy_count

    info_msg = {
        'last_state': last_state,
        'last_id': last_id,
        'free_count': free_count,
        'busy_count': busy_count,
        'last_free_count': last_free_count,
        'last_busy_count': last_busy_count
    }

    return make_response(json.dumps(info_msg), 200, {'Content-Type': 'application/json'})


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
