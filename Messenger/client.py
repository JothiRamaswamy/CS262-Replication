import socket
import curses

from menu import menu
from operations import Operations
from protocols import serialize

PORT = 5050
HEADER = 64
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER_NAME = socket.gethostname() # gets name representing computer on the network
SERVER = socket.gethostbyname(SERVER_NAME) # gets host IPv4 address
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create socket
client.connect(ADDR)

def send(operation, msg):
  serialized_message = serialize({"operation": operation, "info": msg})
  #print(serialized_message)
  message_length = len(serialized_message)
  send_length = str(message_length).encode(FORMAT)
  #print(send_length)
  send_length += b" " * (HEADER - len(send_length))
  #print(send_length)
  client.send(send_length)
  client.send(serialized_message)

  print(client.recv(2048).decode(FORMAT)) # print message received

def start():
  
  # start menu, lets user pick their first action
  actions = ["Login", "Create account", "List accounts", "Delete account"]
  message = "\nWelcome to Messenger! What would you like to do?\n\n"
  name = curses.wrapper(menu, actions, message)

  if name == "Create account":
    print("\nWelcome to messenger! Please input a username to join.\n")
    account_name = input("Username: ")
    if len(account_name) > 10:
      print("\nUsernames must be at most 10 characters.\n")
    else:
      send(Operations.CREATE_ACCOUNT, account_name)

  elif name == "Login": 
    
    # TODO: Add actual login

    # user menu, lets logged-in user pick what they'd like to do
    actions = ["Send messages", "View my messages"]
    message = "\nMy Account\n\n"
    user_choice = curses.wrapper(menu, actions, message)

    if user_choice == "Send messages":
      print("\nInput a message and press enter to share, or type STOP to end the chat.\n")
      while True:
        message = input("Message: ")
        if message == "STOP":
          print(f"\n[ENDING CHAT] Ending chat with {SERVER}\n")
          send(Operations.SEND_MESSAGE, DISCONNECT_MESSAGE)
          break
        send(Operations.SEND_MESSAGE, message)

    elif user_choice == "View my messages": # TODO
      pass

  elif name == "List accounts": # TODO
    pass

  elif name == "Delete account": # TODO
    pass

start()