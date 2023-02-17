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
SEPARATE_CHARACTER = "\n"

USERS = {} # dictionary holding all user objects { key: username, value: user object}

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
        serialized_data = serialize(data)

        send_length = calculate_send_length(serialized_data)
  
        conn.send(send_length)
        conn.send(serialized_data)

      elif operation == Operations.DELETE_ACCOUNT: # client wants to delete
        data = delete_account(info)
        serialized_data = serialize(data)

        send_length = calculate_send_length(serialized_data)
  
        conn.send(send_length)
        conn.send(serialized_data)

      elif operation == Operations.LIST_ACCOUNTS: # client list all
        if not USERS:
          data = {"operation": Operations.FAILURE, "info":""}
          serialized_data = serialize(data)
          send_length = calculate_send_length(serialized_data)
  
          conn.send(send_length)
          conn.send(serialized_data)
        else:
          accounts = USERS.keys()
          accounts_string = "\n".join(accounts)
          data = {"operation": Operations.SUCCESS, "info": accounts_string}
          serialized_data = serialize(data)
          
          send_length = calculate_send_length(serialized_data)
  
          conn.send(send_length)
          conn.send(serialized_data)

      elif operation == Operations.LOGIN: # client login
        data = login(info)
        serialized_data = serialize(data)
        
        send_length = calculate_send_length(serialized_data)
  
        conn.send(send_length)
        conn.send(serialized_data)

      elif operation == Operations.SEND_MESSAGE: # client send message
        if info == DISCONNECT_MESSAGE:
          connected = False
        else:
          info = info.split("\n")
          data = send_message(info[0], info[1], info[2])
          serialized_data = serialize(data)
          send_length = calculate_send_length(serialized_data)
  
          conn.send(send_length)
          conn.send(serialized_data)
          print(f"[{addr}] {version, operation, info}")
          #conn.send("     ... message received by server".encode(FORMAT))

      elif operation == Operations.VIEW_UNDELIVERED_MESSAGES: # client view undelivered
        data = view_msgs(info)
        serialized_data = serialize(data)
        send_length = calculate_send_length(serialized_data)
  
        conn.send(send_length)
        conn.send(serialized_data)
  
  conn.close()

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
  del USERS[username]
  return {"operation": Operations.SUCCESS, "info": ""}

def send_message(sender, receiver, msg):
  USERS[receiver].undelivered_messages.append(msg)
  return {"operation": Operations.SUCCESS, "info": ""}

def view_msgs(username):
  if not USERS[username].undelivered_messages: # handle case of no undelivered messages
    return {"operation": Operations.FAILURE, "info": ""}
  
  messages = SEPARATE_CHARACTER.join(USERS[username].undelivered_messages)
  USERS[username].undelivered_messages = []
  return {"operation": Operations.LIST_OF_MESSAGES, "info": messages}

print("[STARTING] Server is starting at IPv4 Address " + str(SERVER) + " ...")
start()