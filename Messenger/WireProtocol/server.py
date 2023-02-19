# used this tutorial to initially create sockets: https://www.youtube.com/watch?v=3QiPPX-KeSc

import socket
import threading

from operations import Operations
from user import User
from protocols import deserialize, serialize

PORT = 5050
SERVER_NAME = socket.gethostname() # gets name representing computer on the network
SERVER = socket.gethostbyname(SERVER_NAME) # gets host IPv4 address
HEADER = 64
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"
SEPARATE_CHARACTER = "\n"
VERSION = "1"

USER_LOCK = threading.Lock()
USERS = {} # dictionary holding all user objects { key: username, value: user object}
ACTIVE_USERS = {} # holds currently logged in users { key: username, value: conn}

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create socket
server.bind(ADDR)

def handle_client(conn, addr):
  print(f"[NEW CONNECTION] {addr} connected.")

  connected = True
  while connected:
    message_length = conn.recv(HEADER).decode(FORMAT) # length of message (no need to serialize/deserialize)
    if message_length: # check that there actually is a message
      message_length = int(message_length)
      decoded_data = deserialize(conn.recv(message_length)) # message contents, must deserialize

      recv_version = decoded_data["version"] # TODO check client/server version are same
      if recv_version != VERSION:
        print("Wire Protocol Versions do not match")
        connected = False
      operation = decoded_data["operation"]
      info = decoded_data["info"]

      if operation == Operations.CREATE_ACCOUNT: # client wants to create account
        data = create_account(info, conn)
        package_send(data, conn)

      elif operation == Operations.DELETE_ACCOUNT: # client wants to delete
        data = delete_account(info)
        package_send(data, conn)

      elif operation == Operations.LIST_ACCOUNTS: # client list all
        data = list_accounts()
        package_send(data, conn)

      elif operation == Operations.LOGIN: # client login
        data = login(info, conn)
        package_send(data, conn)

      elif operation == Operations.LOGOUT:
        data = logout(info)
        package_send(data, conn)

      elif operation == Operations.SEND_MESSAGE: # client send message
        if info == DISCONNECT_MESSAGE:
          connected = False
          data = payload(Operations.SUCCESS, "")
        else:
          sender, receiver, msg = info.split("\n")
          data = send_message(sender, receiver, msg)
          if receiver in ACTIVE_USERS:
            msg_data = deliver_msgs_immediately(msg)
            package_send(msg_data, ACTIVE_USERS[receiver])
        package_send(data, conn)

      elif operation == Operations.VIEW_UNDELIVERED_MESSAGES: # client view undelivered
        data = view_msgs(info)
        package_send(data, conn)
  
  for key, value in ACTIVE_USERS.items():
    if value == conn:
      del ACTIVE_USERS[key]
      break
  print("close connection")
  conn.close()

def package_send(data, conn):
  serialized_data = serialize(data)
  send_length = calculate_send_length(serialized_data)
  conn.send(send_length)
  conn.send(serialized_data)

def start(): # handle and distribute new connections
  server.listen()
  print(f"[LISTENING] Server is listening on {SERVER}")
  while True:
    conn, addr = server.accept() # blocking line of code
    thread = threading.Thread(target = handle_client, args = (conn, addr))
    thread.start()
    print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

def calculate_send_length(serialized_data):
  message_length = len(serialized_data)
  send_length = str(message_length).encode(FORMAT)
  send_length += b" " * (HEADER - len(send_length))

  return send_length

def login(username, conn):
  with USER_LOCK:
    if username in USERS:
      ACTIVE_USERS[username] = conn
      return payload(Operations.SUCCESS, "")
  return payload(Operations.ACCOUNT_DOES_NOT_EXIST, "")

def logout(username):
  with USER_LOCK:
    if username in ACTIVE_USERS:
      del ACTIVE_USERS[username]
      return payload(Operations.SUCCESS, "")
  return payload(Operations.ACCOUNT_DOES_NOT_EXIST, "")

def create_account(username, conn):
  with USER_LOCK:
    if username in USERS:
      return payload(Operations.ACCOUNT_ALREADY_EXISTS, "")
    new_user = User(username)
    USERS[username] = new_user
    ACTIVE_USERS[username] = conn
  return payload(Operations.SUCCESS, "")

def delete_account(username):
  with USER_LOCK:
    if username in USERS and username in ACTIVE_USERS:
      del USERS[username]
      del ACTIVE_USERS[username]
      return payload(Operations.SUCCESS, "")
    return payload(Operations.ACCOUNT_DOES_NOT_EXIST, "")

def send_message(sender, receiver, msg):
  with USER_LOCK:
    if receiver in USERS:
      if receiver not in ACTIVE_USERS:
        USERS[receiver].queue_message(msg)
      return payload(Operations.SUCCESS, "")
  return payload(Operations.FAILURE, "")

def deliver_msgs_immediately(msg):
  return payload(Operations.RECEIVE_CURRENT_MESSAGE, msg)

def view_msgs(username):
  with USER_LOCK:
    if not USERS[username].undelivered_messages: # handle case of no undelivered messages
      return payload(Operations.FAILURE, "")
  
    messages = SEPARATE_CHARACTER.join(USERS[username].get_current_messages())
  return payload(Operations.SUCCESS, messages)

def list_accounts():
  with USER_LOCK:
    if not USERS:
      return payload(Operations.FAILURE, "")
    else:
      accounts = USERS.keys()
      accounts_string = "\n".join(accounts)
      return payload(Operations.SUCCESS, accounts_string)

def payload(operation, info):
  return {"version": VERSION, "operation": operation, "info": info}

print("[STARTING] Server is starting at IPv4 Address " + str(SERVER) + " ...")
start()