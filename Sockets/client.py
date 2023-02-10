import socket
import curses

from menu import menu

PORT = 5050
HEADER = 64
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER_NAME = socket.gethostname() # gets name representing computer on the network
SERVER = socket.gethostbyname(SERVER_NAME) # gets host IPv4 address
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create socket
client.connect(ADDR)

def send(msg):
  message = msg.encode(FORMAT)
  msg_length = len(message)
  send_length = str(msg_length).encode(FORMAT)
  send_length += b" " * (HEADER - len(send_length))
  client.send(send_length)
  client.send(message)

  # print(client.recv(2048).decode(FORMAT)) # print message received

def start():

  option, name = curses.wrapper(menu)

  print("\nInput a message and press enter to share it with the server. Enter STOP to terminate.\n")
  while True:
    message = input("Message: ")
    if message == "STOP":
      print(f"\n[ENDING CHAT] Ending chat with {SERVER}\n")
      send(DISCONNECT_MESSAGE)
      break
    send(message)

def login():
  pass

start()