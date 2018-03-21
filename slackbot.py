import os
import message
from slackclient import SlackClient

class Bot(object):
    def __init__(self):
        super(Bot, self).__init__()
        self.name = "taskbot"
        self.emoji = ":robot_face:"
        self.oauth = {"client_id": os.environ.get("CLIENT_ID"),
              "client_secret": os.environ.get("CLIENT_SECRET"),
              # Scopes provide and limit permissions to what our app
              # can access. It's important to use the most restricted
              # scope that your app will need.
              "scope": "bot"}
        self.verification = os.environ.get("VERIFICATION_TOKEN")
        self.client = SlackClient(os.environ.get("SLACK_BOT_TOKEN"))

        # We'll use this dictionary to store the state of each message object. - task_id: assigned_by, assigned_to
        self.tasks = {}
        self.task_id_count = 0
    
    def open_dm(self, user_id):
        """
        Open a DM to send a task message when a 'task_request' event is
        recieved from Slack.
        Parameters
        ----------
        user_id : str
            id of the Slack user associated with the 'task_request' event
        Returns
        ----------
        dm_id : str
            id of the DM channel opened by this method
        """
        new_dm = self.client.api_call("im.open",
                                      user=user_id)
        dm_id = new_dm["channel"]["id"]
        return dm_id

    def welcome_message(self, user_id):
        """
        Create and send a welcome message to a new user. Save the
        time stamp of this message on the message object for updating in the
        future.
        Parameters
        ----------
        user_id : str
            id of the new Slack user
        """
        new_message = message.Message()
        new_message.channel = self.open_dm(user_id)
        post_message = self.client.api_call("chat.postMessage",
                                            channel=new_message.channel,
                                            username=self.name,
                                            icon_emoji=self.emoji,
                                            text=new_message.text
                                            )
        new_message.timestamp = post_message["ts"]

    def directions_message(self, user_id):
        new_message = message.DirectionsMessage()
        new_message.channel = self.open_dm(user_id)
        post_message = self.client.api_call("chat.postMessage",
                                            channel=new_message.channel,
                                            username=self.name,
                                            icon_emoji=self.emoji,
                                            text=new_message.text
                                            )
        new_message.timestamp = post_message["ts"]
        
    def show_completed_message(self, task_id):
        completed_by = self.tasks[task_id]['assigned_to']
        assigned_by = self.tasks[task_id]['assigned_by']
        new_message = message.HasCompletedMessage()
        new_message.channel = self.open_dm(completed_by)
        complete_button = [{
            "text": message.AssignTaskMessage(assigned_by, self.tasks[task_id]['content']).text,
            "fallback": "You completed this task",
            "color": "#000000",
            "fields": [
                {
                    "title": "You have completed this task.",
                    "value": "",
                    "short": False
                }
            ]
        }]
        update_message = self.client.api_call("chat.update",
                                            channel=new_message.channel,
                                            text="",
                                            ts= self.tasks[task_id]['message_ts'],
                                            as_user= True,
                                            username=self.name,
                                            icon_emoji=self.emoji,
                                            attachments=complete_button
                                            )
        new_message.timestamp = update_message["ts"]

    def notify_complete_message(self, task_id):
        self.tasks[task_id]['completed'] = True
        send_to = self.tasks[task_id]['assigned_by']
        new_message = message.NotifyTaskCompletedMessage(self.tasks[task_id]['assigned_to'], self.tasks[task_id]['content'])
        new_message.channel = self.open_dm(send_to)
        taskcomplete_notification = [{
            "text": new_message.text,
            "fallback": "{0} completed task {1}".format(self.tasks[task_id]['assigned_to'], task_id),
            "color": "#36a64f"
        }]
        post_message = self.client.api_call("chat.postMessage",
                                            channel=new_message.channel,
                                            username=self.name,
                                            icon_emoji=self.emoji,
                                            text="",
                                            attachments = taskcomplete_notification
                                            )
        new_message.timestamp = post_message["ts"]

    def reply_task_request_message(self, user_id, recipient):
        """
        Create and send a reply message to the user who has requested to assign a task. Save the
        time stamp of this message on the message object for updating in the
        future.
        Parameters
        ----------
        user_id : str
            id of the task assigner user
        """
        new_message = message.ReplyTaskRequestMessage(recipient)
        new_message.channel = self.open_dm(user_id)
        post_message = self.client.api_call("chat.postMessage",
                                            channel=new_message.channel,
                                            username=self.name,
                                            icon_emoji=self.emoji,
                                            text=new_message.text
                                            )
        new_message.timestamp = post_message["ts"]

    def assign_task_message(self, user_id, assigned_by, task):
        """
        Create and send an assign task message to a user. Save the
        time stamp of this message on the message object for updating in the
        future.
        Parameters
        ----------
        user_id : str
            id of the Slack user recieving a task event
        """
        self.task_id_count += 1
        self.tasks[self.task_id_count] = {'assigned_by': assigned_by, 'assigned_to': user_id, 'completed': False, 'content': task}
        message_obj = message.AssignTaskMessage(assigned_by, task)
        message_obj.channel = self.open_dm(user_id)
        #"url": "https://roach.ngrok.io/completed/" + self.task_id_count,
        complete_button = [{
            "text": message_obj.text,
            "fallback": "I am unable to mark this task complete at this time",
            "callback_id": self.task_id_count,
            "color": "#3AA3E3",
            "attachment_type": "default",
            "actions": [
                {
                    "name": "complete_task",
                    "text": "I have completed this task",
                    "type": "button",
                    "value": "complete_task"
                }
            ]
        }]
        post_message = self.client.api_call("chat.postMessage",
                                            channel=message_obj.channel,
                                            username=self.name,
                                            icon_emoji=self.emoji,
                                            text="",
                                            link_names=True,
                                            attachments=complete_button
                                            )
        message_obj.timestamp = post_message["ts"]
        self.tasks[self.task_id_count]['message_ts'] = message_obj.timestamp