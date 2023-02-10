# used this tutorial: https://www.youtube.com/watch?v=3QiPPX-KeSc

import socket
import threading

PORT = 5050
SERVER_NAME = socket.gethostname() # gets name representing computer on the network
SERVER = socket.gethostbyname(SERVER_NAME) # gets host IPv4 address
HEADER = 64
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create socket
server.bind(ADDR)

def handle_client(conn, addr):
  print(f"[NEW CONNECTION] {addr} connected.")

  connected = True
  while connected:
    msg_length = conn.recv(HEADER).decode(FORMAT) # blocking line of code
    if msg_length: # check that there actually is a message
      msg_length = int(msg_length)
      msg = conn.recv(msg_length).decode(FORMAT)

      if msg == DISCONNECT_MESSAGE:
        connected = False

      print(f"[{addr}] {msg}")
      conn.send("Msg received".encode(FORMAT))

def start(): # handle and distribute new connections
  server.listen()
  print(f"[LISTENING] Server is listening on {SERVER}")
  while True:
    conn, addr = server.accept() # blocking line of code
    thread = threading.Thread(target = handle_client, args = (conn, addr))
    thread.start()
    print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


print("[STARTING] Server is starting at IPv4 Address " + str(SERVER) + " ...")
start()