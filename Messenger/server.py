# used this tutorial to initially create sockets: https://www.youtube.com/watch?v=3QiPPX-KeSc

import socket
import threading

from operations import Operations
from classes import user
from protocols import deserialize

PORT = 5050
SERVER_NAME = socket.gethostname() # gets name representing computer on the network
SERVER = socket.gethostbyname(SERVER_NAME) # gets host IPv4 address
HEADER = 64
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

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
        status = create_account(info)["status"]
        if status == Operations.SUCCESS:
          conn.send("     ... account created successfully\n".encode(FORMAT))
          print(USERS)
        else:
          conn.send("\nThe username you have entered already exists. Please try again with another username.\n".encode(FORMAT))
      elif operation == Operations.DELETE_ACCOUNT: # TODO
        status = delete_account(info)["status"]
        if status == Operations.SUCCESS:
          conn.send("     ... account deleted successfully\n".encode(FORMAT))
          print(USERS)
        else:
          conn.send("\nThe username entered does not exist on the server. Please try again.\n".encode(FORMAT))
      elif operation == Operations.LIST_ACCOUNTS: # TODO
        pass
      elif operation == Operations.LOGIN: # TODO
        pass
      elif operation == Operations.SEND_MESSAGE:
        if info == DISCONNECT_MESSAGE:
          connected = False
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

def create_account(username):
  if username in USERS:
    return {"status": Operations.ACCOUNT_ALREADY_EXISTS}
  new_user = user(username)
  USERS[username] = new_user
  return {"status": Operations.SUCCESS}

def delete_account(username):
  if username not in USERS:
    return {"status": Operations.ACCOUNT_DOES_NOT_EXIST}
  del USERS[username]
  return {"status": Operations.SUCCESS}

print("[STARTING] Server is starting at IPv4 Address " + str(SERVER) + " ...")
start()