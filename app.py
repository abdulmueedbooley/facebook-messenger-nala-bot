import os
import sys
import json
from datetime import datetime

import requests
from flask import Flask, request

app = Flask(__name__)

def log(msg):
    print(str(msg))
    sys.stdout.flush()

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == "nala_booley_2019": # Enter tokon here
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # this means someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"].get("text", "")  # the message's text

                    user_msg = message_text.lower().strip() # made text lower case and removed any unneccessary spacing

                    if any(word in user_msg for word in ["hi", "hello", "hey"]): # any of these strings are found in the text body
                        send_message(sender_id, "Meow-llo! My name is Nala Booley.")

                    elif any(word in user_msg for word in ["food", "eat", "hungry", "pampers"]):
                        send_message(sender_id, "Iam a fat cat and I LOVE FOOD. My favourite brand is PAMPERS seafood flavour!!!")

                    elif any(word in user_msg for word in ["breed", "kind", "type"]):
                        send_message(sender_id, "Iam a colourful ginger cat. A good representation would be a Calico cat.")

                    else:
                        #DEFAULT RESPONSE
                        send_message(sender_id, f"Nala heard you say: '{message_text}'")

    return "ok", 200


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": "EAAo3GbZBmHVMBSRTzTtKRQ5jluhyKDRQ83QpZAGjngXj7KwXO7UcHEtbWmwzsvOvBCrogezg18638s8PQiV0mP3PErAfs0rQJpOXB2uZARuf3BdfIvFDDq6Mg6LEYWSgWnbRWNcNIvquZCKOpLmvmfSAEYLX6phr3WLMJj1UGBx50GyGuxRIejcKO5rtFNZBUTT8ytQZDZD"
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(msg, *args, **kwargs):  # simple wrapper for logging to stdout on heroku
    try:
        if type(msg) is dict:
            msg = json.dumps(msg)
        else:
            msg = str(msg).format(*args, **kwargs)
        print("{}: {}".format(datetime.now(), msg))
    except Exception:
        pass
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
