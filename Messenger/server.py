# used this tutorial to initially create sockets: https://www.youtube.com/watch?v=3QiPPX-KeSc

import socket
import threading

from operations import Operations
from classes import user
from protocols import deserialize, serialize

PORT = 5050
SERVER_NAME = socket.gethostname() # gets name representing computer on the network
SERVER = socket.gethostbyname(SERVER_NAME) # gets host IPv4 address
HEADER = 64
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

USERS = {"jothi": user("jothi")} # dictionary holding all user objects { key: username, value: user object}

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

      version = decoded_data["version"] # TODO check client/server version are same
      operation = decoded_data["operation"]
      info = decoded_data["info"]

      if operation == Operations.CREATE_ACCOUNT: # client wants to create account
        data = create_account(info)
        serialize_data = serialize(data)
        conn.send(serialize_data)
        # if status == Operations.SUCCESS:
        #   conn.send("     ... account created successfully\n".encode(FORMAT))
        #   print(USERS)

           # TODO: communicate with client what happened on server

        # else:
        #   conn.send("\nThe username you have entered already exists. Please try again with another username.\n".encode(FORMAT))
      elif operation == Operations.DELETE_ACCOUNT: # TODO
        pass
      elif operation == Operations.LIST_ACCOUNTS: # TODO
        pass
      elif operation == Operations.LOGIN: # TODO
        data = login(info)
        serialize_data = serialize(data)
        conn.send(serialize_data)
      elif operation == Operations.SEND_MESSAGE:
        if info == DISCONNECT_MESSAGE:
          connected = False
        info = info.split("\n")
        data = send_message(info[0], info[1], info[2])
        serialize_data = serialize(data)
        conn.send(serialize_data)
        print(f"[{addr}] {version, operation, info}")
        conn.send("     ... message received by server".encode(FORMAT))
  
  conn.close()

def start(): # handle and distribute new connections
  server.listen()
  print(f"[LISTENING] Server is listening on {SERVER}")
  while True:
    conn, addr = server.accept() # blocking line of code
    thread = threading.Thread(target = handle_client, args = (conn, addr))
    thread.start()
    print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

def login(username):
    if username in USERS:
        print(USERS[username].undelivered_messages)
        return {"operation": Operations.SUCCESS, "info": ""}
    return {"operation": Operations.ACCOUNT_DOES_NOT_EXIST, "info": ""}

def create_account(username):
    if username in USERS:
      return {"operation": Operations.ACCOUNT_ALREADY_EXISTS, "info": ""}
    new_user = user(username)
    USERS[username] = new_user
    return {"operation": Operations.SUCCESS, "info":""}

def delete_account(username):
    if username in USERS:
        USERS.pop(username)
        return {"operation": Operations.SUCCESS}
    return {"operation": Operations.ACCOUNT_DOES_NOT_EXIST, "info": ""}

def list_accounts():
    user_list = pickle.dumps(list(USERS.keys()))
    return {"operation": Operations.LIST_OF_ACCOUNTS, "info": user_list}

def send_message(sender, receiver, msg):
  print(receiver, sender)
  if receiver in USERS and sender in USERS:
      USERS[receiver].undelivered_messages.append(msg)
      return {"operation": Operations.SUCCESS, "info": ""}
  return {"operation": Operations.ACCOUNT_DOES_NOT_EXIST, "info": ""}

def view_msgs(username):
    if username in USERS:
        messages = pickle.dumps(USERS[username].undelivered_messages)
        USERS[username].undelivered_messages.clear()
        return {"operation": Operations.LIST_OF_MESSAGES, "info": messages}
    return {"operation": Operations.ACCOUNT_DOES_NOT_EXIST, "info": ""}


print("[STARTING] Server is starting at IPv4 Address " + str(SERVER) + " ...")
start()