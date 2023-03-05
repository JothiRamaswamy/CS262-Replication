from queue import Queue


class User:
  def __init__(self, username):
    self.username = username
    self.undelivered_messages = Queue()

  def queue_message(self, message):
    self.undelivered_messages.put(message)

  def get_current_messages(self):
    messages = []
    while self.undelivered_messages.empty() == False:
      messages.append(self.undelivered_messages.get())
    return messages