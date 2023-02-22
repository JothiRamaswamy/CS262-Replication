# used this tutorial to initially create sockets: https://www.youtube.com/watch?v=3QiPPX-KeSc

import socket
import threading

from operations import Operations
from user import User
from protocols import deserialize, serialize

class WireServer:

  """
  Initializes the server object with necessary configurations.
  """

  PORT = 5050
  SERVER_HOST_NAME = socket.gethostname() # gets name representing computer on the network
  SERVER_HOST = socket.gethostbyname(SERVER_HOST_NAME) # gets host IPv4 address
  HEADER = 64
  ADDR = (SERVER_HOST, PORT)
  FORMAT = "utf-8"
  DISCONNECT_MESSAGE = "!DISCONNECT"
  SEPARATE_CHARACTER = "\n"
  VERSION = "1"

  USER_LOCK = threading.Lock()
  USERS = {} # dictionary holding all user objects { key: username, value: user object}
  ACTIVE_USERS = {} # holds currently logged in users { key: username, value: conn}

  SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create socket

  def handle_client(self, conn, addr):
    """
    Handles incoming connections from clients.

    Parameters:
    conn (socket.socket): Socket object representing the connection to the client.
    addr (str, int): IP address and port number of the client.

    Returns: None
    """
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
      message_length = conn.recv(self.HEADER).decode(self.FORMAT) # length of message (no need to serialize/deserialize)
      if message_length: # check that there actually is a message
        message_length = int(message_length)
        decoded_data = deserialize(conn.recv(message_length)) # message contents, must deserialize

        recv_version = decoded_data["version"] # TODO check client/server version are same
        if recv_version != self.VERSION:
          print("Wire Protocol Versions do not match")
          connected = False
        operation = decoded_data["operation"]
        info = decoded_data["info"]

        if operation == Operations.CREATE_ACCOUNT: # client wants to create account
          data = self.create_account(info, conn)
          self.package_send(data, conn)

        elif operation == Operations.DELETE_ACCOUNT: # client wants to delete
          data = self.delete_account(info)
          self.package_send(data, conn)

        elif operation == Operations.LIST_ACCOUNTS: # client list all
          data = self.list_accounts()
          self.package_send(data, conn)

        elif operation == Operations.LOGIN: # client login
          data = self.login(info, conn)
          self.package_send(data, conn)

        elif operation == Operations.LOGOUT:
          data = self.logout(info)
          self.package_send(data, conn)

        elif operation == Operations.SEND_MESSAGE: # client send message
          if info == self.DISCONNECT_MESSAGE:
            connected = False
            data = self.payload(Operations.SUCCESS, "")
          else:
            sender, receiver, msg = info.split("\n")
            data = self.send_message(sender, receiver, msg)
            if receiver in self.ACTIVE_USERS:
              msg_data = self.deliver_msgs_immediately(msg)
              self.package_send(msg_data, self.ACTIVE_USERS[receiver])
          self.package_send(data, conn)

        elif operation == Operations.VIEW_UNDELIVERED_MESSAGES: # client view undelivered
          data = self.view_msgs(info)
          self.package_send(data, conn)
    
    for key, value in self.ACTIVE_USERS.items():
      if value == conn:
        del self.ACTIVE_USERS[key]
        break
    conn.close()

  def package_send(self, data, conn):
    """
    Serializes and sends data to the specified connection

    Args:
        data (Any): The data to be serialized and sent
        conn (socket.socket): The socket connection to send the serialized data to

    Returns:
        None
    """
    serialized_data = serialize(data)
    send_length = self.calculate_send_length(serialized_data)
    conn.send(send_length)
    conn.send(serialized_data)

  def start(self):
    """
    Starts the server and handles incoming connections by creating a new thread for each connection

    Args:
        None

    Returns:
        None
    """
    print("[STARTING] Server is starting at IPv4 Address " + str(self.SERVER_HOST) + " ...")
    self.SERVER.listen()
    print(f"[LISTENING] Server is listening on {self.SERVER_HOST}")
    while True:
      conn, addr = self.SERVER.accept() # blocking line of code
      thread = threading.Thread(target = self.handle_client, args = (conn, addr))
      thread.start()
      print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

  def calculate_send_length(self, serialized_data):
    """
    Calculates the length of the serialized data and returns a bytes object that represents the length

    Args:
        serialized_data (bytes): The serialized data to calculate the length of

    Returns:
        bytes: A bytes object that represents the length of the serialized data
    """
    message_length = len(serialized_data)
    send_length = str(message_length).encode(self.FORMAT)
    send_length += b" " * (self.HEADER - len(send_length))

    return send_length

  def login(self, username, conn):
    """
    Logs a user in by adding their connection to the list of active users

    Args:
        username (str): The username of the user to log in
        conn (socket.socket): The socket connection of the user to log in

    Returns:
        Dict[str, Any]: A dictionary that represents the payload of the login operation
    """
    with self.USER_LOCK:
      if username in self.USERS:
        self.ACTIVE_USERS[username] = conn
        return self.payload(Operations.SUCCESS, "")
    return self.payload(Operations.ACCOUNT_DOES_NOT_EXIST, "")

  def logout(self, username):
    """
    Logs a user out by removing their connection from the list of active users

    Args:
        username (str): The username of the user to log out

    Returns:
        A dictionary that represents the payload of the logout operation
    """
    with self.USER_LOCK:
      if username in self.ACTIVE_USERS:
        del self.ACTIVE_USERS[username]
        return self.payload(Operations.SUCCESS, "")
    return self.payload(Operations.ACCOUNT_DOES_NOT_EXIST, "")

  def create_account(self, username, conn):
    """
    Creates a new account for the specified user and adds their connection to the list of active users

    Args:
        username (str): The username of the user to create an account for
        conn (socket.socket): The socket connection of the user to add to the list of active users

    Returns:
        A dictionary that represents the payload of the create account operation
    """
    with self.USER_LOCK:
      if username in self.USERS:
        return self.payload(Operations.ACCOUNT_ALREADY_EXISTS, "")
      new_user = User(username)
      self.USERS[username] = new_user
      self.ACTIVE_USERS[username] = conn
    return self.payload(Operations.SUCCESS, "")

  def delete_account(self, username):
    """
    Deletes an account with the given username.

    Args:
        username (str): The username of the account to delete.

    Returns:
        dict: A dictionary containing the version, operation, and info fields
        of the payload. If the account is successfully deleted, the operation is
        set to Operations.SUCCESS and the info field is an empty string. If the
        account does not exist, the operation is set to
        Operations.ACCOUNT_DOES_NOT_EXIST and the info field is an empty string.
    """
    with self.USER_LOCK:
      if username in self.USERS and username in self.ACTIVE_USERS:
        del self.USERS[username]
        del self.ACTIVE_USERS[username]
        return self.payload(Operations.SUCCESS, "")
      return self.payload(Operations.ACCOUNT_DOES_NOT_EXIST, "")

  def send_message(self, sender, receiver, msg):
    """
    Sends a message from a sender to a receiver.

    Args:
        sender (str): The username of the sender.
        receiver (str): The username of the receiver.
        msg (str): The message to send.

    Returns:
        dict: A dictionary containing the version, operation, and info fields
        of the payload. If the message is successfully sent, the operation is
        set to Operations.SUCCESS and the info field is an empty string. If the
        receiver does not exist or is not currently active, the operation is set
        to Operations.FAILURE and the info field is an empty string.
    """
    with self.USER_LOCK:
      if receiver in self.USERS:
        if receiver not in self.ACTIVE_USERS:
          self.USERS[receiver].queue_message(msg)
        return self.payload(Operations.SUCCESS, "")
    return self.payload(Operations.FAILURE, "")

  def deliver_msgs_immediately(self, msg):
    """
    Delivers a message to the recipient immediately.

    Args:
        msg (str): The message to deliver.

    Returns:
        dict: A dictionary containing the version, operation, and info fields
        of the payload. The operation is set to Operations.RECEIVE_CURRENT_MESSAGE
        and the info field contains the message to deliver.
    """
    return self.payload(Operations.RECEIVE_CURRENT_MESSAGE, msg)

  def view_msgs(self, username):
    """
    Retrieves the undelivered messages for a given user.

    Args:
        username (str): The username of the user.

    Returns:
        dict: A dictionary containing the version, operation, and info fields
        of the payload. If the user has no undelivered messages, the operation
        is set to Operations.FAILURE and the info field is an empty string. If
        the user has undelivered messages, the operation is set to
        Operations.SUCCESS and the info field contains a string with the
        messages separated by the SEPARATE_CHARACTER.
    """
    with self.USER_LOCK:
      if self.USERS[username].undelivered_messages.empty(): # handle case of no undelivered messages
        return self.payload(Operations.FAILURE, "")
    
      messages = self.SEPARATE_CHARACTER.join(self.USERS[username].get_current_messages())
    return self.payload(Operations.SUCCESS, messages)

  def list_accounts(self):
    """
    Lists all accounts.

    Returns:
        dict: A dictionary containing the version, operation, and info fields
        of the payload. If there are no accounts, the operation is set to
        Operations.FAILURE and the info field is an empty string. If there are
        accounts, the operation is set to Operations.SUCCESS and the info field
        contains a string with the usernames separated by a newline character.
    """
    with self.USER_LOCK:
      if len(self.USERS) == 0:
        return self.payload(Operations.FAILURE, "")
      else:
        accounts = self.USERS.keys()
        accounts_string = "\n".join(accounts)
        return self.payload(Operations.SUCCESS, accounts_string)

  def payload(self, operation, info):
    """
    Creates a payload dictionary.

    Args:
        operation (str): The operation to perform.
        info (str): The information to include in the payload.

    Returns:
        dict: A dictionary containing the version, operation, and info fields.
    """
    return {"version": self.VERSION, "operation": operation, "info": info}