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
from sensorsdata import SensorsData
import time
from datetime import datetime
import math
import random
import os

pyBot = bot.Bot()
slack = pyBot.client
queue = DummyToiletQueue()
last_state = 0
last_id = 0
free_count = 0
busy_count = 0
last_free_count = 0
last_busy_count = 0

sensorsData = SensorsData()

app = Flask(__name__)

already_in_queue = [u"<@%s> ты уже %s в очереди", u"%<@%s> заебал, ты уже %s очереди", u"<@%s>скоро уже, ты %s :tada:"]
in_queue = [u"<@%s> аеее! ты %s в очереди", u"<@%s> заебись! ты в очереди!", u"<@%s> аеее! ты %s в очереди", u"<@%s> поздравляю, ты %s :tada:"]
not_in_queue = [u"<@%s> чё? ты не записан", u"<@%s> хули ты пишешь? ты не в очереди!", u"<@%s> сначала запишись!", u"<@%s>просто попроси нормально, и я тебя запишу"]
gth = [u"<@%s> Ебись", u"<@%s> Ты ебанулся?", u"<@%s> ты ебанулся пидор?!?!?", u"<@%s> Хуй положи на кактус, вдруг отпустит", u"<@%s> вон туда сходи, хуйли сюда стремишься", u"<@%s> Ты мне ещё предложи кого-то из двух годичной очереди позвать", u"<@%s> у меня такое гавно как ты толчки не расчитаны", u"<@%s> не для тебя я свои очереди готовила", u"<@%s> не для тебя толчки драили, пидор", u"ту-ту-ту, хуй во рту", u"<@%s> блогаславляю тебя на вечное воздержание", u"<@%s> Изящно на хуй иди", u"<@%s> Не ебет, жди", u"<@%s> Бахни пока https://rt.pornhub.com/video/search?search=pornohub", u"<@%s> тут таких как ты до ебени", u"<@%s> Донат решает, 5 баксов и ты в топе", u"<@%s> 10 тыщ пыдыщ и ты идешь на хер", u"<@%s> Ебанутый штоли?", u"<@%s> Засунь свою толерантность в жопу и ебись", u"<@%s> Вот охотники за приведениями терпели, и ты терпи", u"<@%s> Ебашь да не наебашь в шортики", u"<@%s> лучше бы обувь переодел", u"<@%s> Фриидом кам, но не скоро"]
oh_my_god = [u"<@%s> Ты заебал, блять, терпи сука", u"<@%s> Че началось, то! терпи бля", u"<@%s> Терпи нормально, нормально будет", u"<@%s> прости сука, все будет, но позже", u"<@%s> Да мне похуй, терпи!", u"<@%s> Ну допустим, я что я должен сделать?", u"<@%s> Вот сейчас обидно было", u"<@%s> Вот сейчас обидно было", u"<@%s> Кто тебя этому научил?", u"<@%s> так неловко", u"<@%s> бля"]
hz = [u"<@%s> Я ни хуя не понял", u"<@%s> Чё те надо, заебал?", u"<@%s> Говори нормально, уёбок", u"<@%s> Нихуя не понятно", u"<@%s>Ты сам то понял, что написал?", u"<@%s>Что то не разборчиво"]

def book(user_id, channel):
    global queue
    if channel in queue.get():
        st = queue.get_my_status(channel)
        #message = "<@%s> You are pidor and you are already in the queue! You're the %s" % (user_id, st)
        message = random.choice(already_in_queue) % (user_id, st)
    else:
        queue.add(channel)
        st = queue.get_my_status(channel)
        #message = "<@%s> You booked! You're the %d's in the queue :tada:" % (user_id, st)
        message = random.choice(in_queue) % (user_id, st)
    pyBot.direct_message(message, channel)


def check_status(user_id, channel):
    global queue
    st = queue.get_my_status(channel)
    if st != -1:
        #message = "<@%s> You're the %s in the queue :tada:" % (user_id, st)
        message = random.choice(in_queue) % (user_id, st)
    else:
        #message = "<@%s> You're not in the queue (because you are pidor)" % user_id
        message = random.choice(not_in_queue) % (user_id, st)
    pyBot.direct_message(message, channel)


def go_to_hell(user_id, channel):
    #message = "<@%s> Fuck You! Nu ty i pidor! :tada:" % user_id
    message = random.choice(gth) % (user_id)
    pyBot.direct_message(message, channel)


def omg(user_id, channel):
    #message = "<@%s> OMG! :tada:" % user_id
    message = random.choice(oh_my_god) % (user_id)
    pyBot.direct_message(message, channel)


def other(user_id, channel):
    #message = "<@%s> Nu ya hui znaet :tada:" % user_id
    message = random.choice(hz) % (user_id)
    pyBot.direct_message(message, channel)


def _save_to_file(ml_dict, path):
    with open(path, "a+") as f:
        f.write(json.dumps(ml_dict))
        f.write('\n')


def _event_handler(event_type, slack_event):
    team_id = slack_event["team_id"]
    user_id = slack_event["event"].get("user")

    if event_type == "message" and user_id is not None:
        token = slack_event["token"]
        channel = slack_event["event"].get("channel")
        in_message = {
            "msg": [slack_event.get("event", {}).get("text", "")]
        }
        try:
            ml_request = requests.post(pyBot.nlp_http, json=in_message)

            # ml_request example = {"input_length": [5], "confidences": [
            #     [0.9999997615814209, 9.267279998947942E-11, 1.517895698022187E-9, 2.1478415135334217E-7,
            #      1.9579935894853406E-8, 2.6716921792849062E-14]],
            #  "intents": ["Book", "CheckStatus", "GoToHell", "OMG", "Fail", "Other"]}

            intent_labels = {
                'Book': book,
                'CheckStatus': check_status,
                'GoToHell': go_to_hell,
                'OMG': omg,
                'Other': other
            }

            confidences = ml_request.json().get('confidences')[0]
            max_confidence = max(confidences)

            n = float(len(confidences))
            x_median = math.fsum(confidences) / n
            D = math.fsum([math.pow(x - x_median, 2.0) for x in confidences]) / n
            sigma = math.sqrt(D)
            print sigma, D, x_median, n
            if sigma < 0.11:
                intent = 'Other'
            else:
                index_max_confidence = [i for i, j in enumerate(confidences) if j == max_confidence][0]
                intent = ml_request.json().get('intents')[index_max_confidence]

            dialect = intent_labels.get(intent)
            dialect(user_id, channel)

            # _save_to_file({
            #     "in_message": in_message,
            #     "ml_request": ml_request.json(),
            #     "intent": intent
            # }, "/data/bluewater_ml_messages.json")

        except Exception as error_message:
            print error_message
            book(user_id, channel)

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
        status = int(data.get('status', 0))
        ident = int(data.get('sec', 0))
        now = int(datetime.utcnow().strftime("%s"))

        if ident > (now+150):
            print 'time in hardware > now'
        else:
            if ((busy_count > 3600) or (free_count > 20) or (status is 1 and last_state is 0 and busy_count > 5)) and last_id < ident:
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
            else:
                pass

        # sensorsData.append(sec=data.get('sec', 0), data=data)

    except Exception as e:
        print 'error', sys.exc_info()[0]
        raise e
    return make_response("Ok.", 200, )


@app.route("/clean_sensors_data", methods=["GET"])
def clean_sensors():
    sensorsData.delete()
    return make_response("Clean: 'success'", 200, {'Content-Type': 'application/json'})


@app.route("/get_sensors", methods=["GET"])
def get_sensors():
    try:
        offset = request.args.get('offset', 0)
        limit = request.args.get('limit', 100)
        pattern = request.args.get('pattern', "sensors*")
        data = sensorsData.get(offset=offset, limit=limit, pattern=pattern)
        return make_response(json.dumps(data), 200, {'Content-Type': 'application/json'})
    except Exception as e:
        return make_response("oops: %s" % sys.exc_info()[0], 200, {'Content-Type': 'application/json'})


@app.route("/get_sensors_latest", methods=["GET"])
def get_sensors_latest():
    try:
        offset = request.args.get('offset', 0)
        limit = request.args.get('limit', 100)
        pattern = request.args.get('pattern', "sensors*")
        data = sensorsData.get_latest(offset=offset, limit=limit, pattern=pattern)
        return make_response(json.dumps(data), 200, {'Content-Type': 'application/json'})
    except Exception as e:
        return make_response("oops: %s" % sys.exc_info()[0], 200, {'Content-Type': 'application/json'})


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
        'last_busy_count': last_busy_count,
        'server_time': int(time.time()),
        'utc_server_time': int(datetime.utcnow().strftime("%s"))
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
