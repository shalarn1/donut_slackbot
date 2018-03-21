from flask import Flask, request, make_response, render_template
import json
import slackbot

pyBot = slackbot.Bot()
slack = pyBot.client

app = Flask(__name__)

def _event_handler(event_type, slack_event):
    """
    A helper function that routes events from Slack to our Bot
    by event type and subtype.
    """
    # ================ Team Join Events =============== #
    # When the user first joins a team, the type of event will be team_join
    if event_type == "team_join":
        user_id = slack_event["event"]["user"]["id"]
        # Send the onboarding message
        pyBot.welcome_message(user_id)
        return make_response("Welcome Message Sent", 200,)

    # ================ Incoming Message Events =============== #
    # When the bot recieves a message from a user, the type of event will be message
    if event_type == "message" and not slack_event["event"].get('bot_id'):
        # not message changed
        if not slack_event["event"].get("subtype"):
            user_id = slack_event["event"]["user"]
            full_message = slack_event["event"]["text"].split(' ', 1)
            assigned_to_raw = full_message[0].strip('<').strip('>')
            if assigned_to_raw[0] != "@":
                pyBot.directions_message(user_id)
                return make_response("Directions Message Sent", 200,)
            else:
                assigned_to = assigned_to_raw[1:]
            task = full_message[1]
            assigned_by = user_id
            # Send the assignment messages
            pyBot.assign_task_message(assigned_to, assigned_by, task)
            pyBot.reply_task_request_message(assigned_by, assigned_to)
            return make_response("Direct Message Sent", 200,)

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})

@app.route("/complete_task", methods=["GET", "POST"])
def test():
    form_json = json.loads(request.form["payload"])
    task_id = int(form_json['callback_id'])
    pyBot.notify_complete_message(task_id)
    pyBot.show_completed_message(task_id)
    return make_response("", 200,)

@app.route("/listening", methods=["GET", "POST"])
def hears():
    """
    This route listens for incoming events from Slack and uses the event
    handler helper function to route events to our Bot.
    """
    slack_event = json.loads(request.data)

    # ============= Slack URL Verification ============ #
    # In order to verify the url of our endpoint, Slack will send a challenge
    # token in a request and check for this token in the response our endpoint
    # sends back.
    #       For more info: https://api.slack.com/events/url_verification
    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                             "application/json"
                                                             })
    # ============ Slack Token Verification =========== #
    # We can verify the request is coming from Slack by checking that the
    # verification token in the request matches our app's settings
    if pyBot.verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s \npyBot has: \
                   %s\n\n" % (slack_event["token"], pyBot.verification)
        # By adding "X-Slack-No-Retry" : 1 to our response headers, we turn off
        # Slack's automatic retries during development.
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    # ====== Process Incoming Events from Slack ======= #
    # If the incoming request is an Event we've subcribed to
    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        # Then handle the event by event_type and have your bot respond
        return _event_handler(event_type, slack_event)
    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})

if __name__ == '__main__':
    app.run(debug=True)