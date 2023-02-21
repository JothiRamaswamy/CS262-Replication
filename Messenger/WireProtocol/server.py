# used this tutorial to initially create sockets: https://www.youtube.com/watch?v=3QiPPX-KeSc

import socket
import threading

from operations import Operations
from user import User
from protocols import deserialize, serialize

class WireServer:

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
    serialized_data = serialize(data)
    send_length = self.calculate_send_length(serialized_data)
    conn.send(send_length)
    conn.send(serialized_data)

  def start(self): # handle and distribute new connections
    print("[STARTING] Server is starting at IPv4 Address " + str(self.SERVER_HOST) + " ...")
    self.SERVER.listen()
    print(f"[LISTENING] Server is listening on {self.SERVER_HOST}")
    while True:
      conn, addr = self.SERVER.accept() # blocking line of code
      thread = threading.Thread(target = self.handle_client, args = (conn, addr))
      thread.start()
      print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

  def calculate_send_length(self, serialized_data):
    message_length = len(serialized_data)
    send_length = str(message_length).encode(self.FORMAT)
    send_length += b" " * (self.HEADER - len(send_length))

    return send_length

  def login(self, username, conn):
    with self.USER_LOCK:
      if username in self.USERS:
        self.ACTIVE_USERS[username] = conn
        return self.payload(Operations.SUCCESS, "")
    return self.payload(Operations.ACCOUNT_DOES_NOT_EXIST, "")

  def logout(self, username):
    with self.USER_LOCK:
      if username in self.ACTIVE_USERS:
        del self.ACTIVE_USERS[username]
        return self.payload(Operations.SUCCESS, "")
    return self.payload(Operations.ACCOUNT_DOES_NOT_EXIST, "")

  def create_account(self, username, conn):
    with self.USER_LOCK:
      if username in self.USERS:
        return self.payload(Operations.ACCOUNT_ALREADY_EXISTS, "")
      new_user = User(username)
      self.USERS[username] = new_user
      self.ACTIVE_USERS[username] = conn
    return self.payload(Operations.SUCCESS, "")

  def delete_account(self, username):
    with self.USER_LOCK:
      if username in self.USERS and username in self.ACTIVE_USERS:
        del self.USERS[username]
        del self.ACTIVE_USERS[username]
        return self.payload(Operations.SUCCESS, "")
      return self.payload(Operations.ACCOUNT_DOES_NOT_EXIST, "")

  def send_message(self, sender, receiver, msg):
    with self.USER_LOCK:
      if receiver in self.USERS:
        if receiver not in self.ACTIVE_USERS:
          self.USERS[receiver].queue_message(msg)
        return self.payload(Operations.SUCCESS, "")
    return self.payload(Operations.FAILURE, "")

  def deliver_msgs_immediately(self, msg):
    return self.payload(Operations.RECEIVE_CURRENT_MESSAGE, msg)

  def view_msgs(self, username):
    with self.USER_LOCK:
      if self.USERS[username].undelivered_messages.empty(): # handle case of no undelivered messages
        return self.payload(Operations.FAILURE, "")
    
      messages = self.SEPARATE_CHARACTER.join(self.USERS[username].get_current_messages())
    return self.payload(Operations.SUCCESS, messages)

  def list_accounts(self):
    with self.USER_LOCK:
      if not self.USERS:
        return self.payload(Operations.FAILURE, "")
      else:
        accounts = self.USERS.keys()
        accounts_string = "\n".join(accounts)
        return self.payload(Operations.SUCCESS, accounts_string)

  def payload(self, operation, info):
    return {"version": self.VERSION, "operation": operation, "info": info}