class Message(object):
    """
    Instanciates a Message object to create and manage
    Slack messages.
    """
    def __init__(self):
        super(Message, self).__init__()
        self.channel = ''
        self.timestamp = ''
        self.text = 'Hello! Welcome to Slack! I am a Task Manager Bot. Assign tasks to your teammates in this channel by sending me @tagged_user [task]. Ex @joe Fix bug.'

class DirectionsMessage(Message):
    def __init__(self):
        super(Message, self).__init__()
        self.channel = ''
        self.timestamp = ''
        self.text = 'Please assign tasks to your teammates in this channel by sending me @user [task]. Ex. @joe Clean Dishes.'

class ReplyTaskRequestMessage(Message):
    """
    Instanciates a Message object to create and manage
    a reply to a Task Request message.
    """
    def __init__(self, user_id):
        super(Message, self).__init__()
        self.text = ("Ok. I have assigned that task to {0}. I will let you know when the task has been completed.".format(user_id))

class NotifyTaskCompletedMessage(Message):
    """
    Instanciates a Message object to create and manage
    Slack task done messages.
    Parameters
        ----------
        user_id : str
            id of the Slack user that filed the 'task_request' event
    """
    def __init__(self, completed_by, task):
        super(Message, self).__init__()
        self.text = ("{0} completed the task:\n{1}".format(completed_by, task))

class HasCompletedMessage(Message):
    def __init__(self):
        super(Message, self).__init__()
        self.text = ("You have completed this task.")

class AssignTaskMessage(Message):
    """
    Instanciates a Message object to create and manage
    Slack assign task messages.
    Parameters
        ----------
        user_id : str
            id of the Slack user that assigned the 'task_request' event
    """
    def __init__(self, user_id, task):
        super(Message, self).__init__()
        self.text = ("{0} assigned you the following task:\n\n{1}".format(user_id, task))