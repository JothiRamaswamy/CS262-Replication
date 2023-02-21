from queue import Queue


class User:
  def __init__(self, username):
    self.username = username
    self.logged_in = True
    self.undelivered_messages = Queue()
    self.immediate_messages = Queue()

  def queue_message(self, message, deliver_now=False):
    if deliver_now:
      self.immediate_messages.put(message)
    else:
      self.undelivered_messages.put(message)

  def get_current_messages(self, deliver_now=False):
    messages = []
    if deliver_now:
      while self.immediate_messages.empty() == False:
        messages.append(self.immediate_messages.get())
    else:
      while self.undelivered_messages.empty() == False:
        messages.append(self.undelivered_messages.get())
    return messages