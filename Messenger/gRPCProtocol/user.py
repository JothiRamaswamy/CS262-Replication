from queue import Queue


class User:
    def __init__(self, username):
        """
        Initializes a User object with the given username and default attributes.

        Args:
        - username (str): The username of the user.

        Returns:
        None
        """
        # Initialize username and if the user is actively logged in
        self.username = username
        self.logged_in = True
        # Create a queue for messages when the user is logged out
        self.undelivered_messages = Queue()
        # Create a queue for messages when the user is logged in
        self.immediate_messages = Queue()

    def queue_message(self, message, deliver_now=False):
        """
        Queues the given message in either the immediate or undelivered messages queue.

        Args:
        - message (str): The message to be queued.
        - deliver_now (bool): Determines whether the message should be delivered immediately. Defaults to False.

        Returns:
        None
        """
        # if it should be delivered now, put in immediate_messages
        if deliver_now:
            self.immediate_messages.put(message)
        # otherwise, put in undelivered_messages
        else:
            self.undelivered_messages.put(message)

    def get_current_messages(self, deliver_now=False):
        """
        Returns a list of messages in either the immediate or undelivered messages queue.

        Args:
        - deliver_now (bool): Determines whether the message should be delivered immediately. Defaults to False.

        Returns:
        A list of messages in either the immediate or undelivered messages queue.
        """
        # stores messages popped from queue to be returned
        messages = []
        # if it should be delivered now, get from immediate_messages
        if deliver_now:
            while self.immediate_messages.empty() == False:
                messages.append(self.immediate_messages.get())
        # otherwise, get from undelivered_messages
        else:
            while self.undelivered_messages.empty() == False:
                messages.append(self.undelivered_messages.get())
        return messages