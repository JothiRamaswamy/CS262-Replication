import socket
import curses

from menu import menu
from operations import Operations
from protocols import serialize, deserialize

PORT = 5050
HEADER = 64
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER_NAME = socket.gethostname() # gets name representing computer on the network
SERVER = socket.gethostbyname(SERVER_NAME) # gets host IPv4 address
ADDR = (SERVER, PORT)
CURRENT_USER = [""]

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create socket
client.connect(ADDR)

def send(operation, msg):
  serialized_message = serialize({"operation": operation, "info": msg})
  message_length = len(serialized_message)
  send_length = str(message_length).encode(FORMAT)
  send_length += b" " * (HEADER - len(send_length))
  client.send(send_length)
  client.send(serialized_message)

  return client.recv(2048) # print message received

def login(username):
    received_info = send(Operations.LOGIN, username)
    print(received_info)
    status = deserialize(received_info)["operation"]
    if status == "00":
      CURRENT_USER[0] = username
      return 0
    print("Account information does not exist")
    return 1

def create_account(username):
    received_info = send(Operations.CREATE_ACCOUNT, username)
    status = deserialize(received_info)["operation"]
    if status == "00":
      CURRENT_USER[0] = username
      return 0
    print("Account information already exists")
    return 1

def delete_account(username):
    received_info = send(Operations.DELETE_ACCOUNT, username)
    status = deserialize(received_info)["operation"]
    if status == "00":
        CURRENT_USER[0] = ""
        start()
        return
    print("Deletion Unsuccessful")
    return 1

def list_accounts():
    data = {"operation": Operations.LIST_ACCOUNT, "info": ""}
    new_data = serialize(data)
    received_info = send(new_data)
    status = deserialize(received_info)["operation"]
    if status == "03":
        return deserialize(received_info)["info"]
    print("Account information does not exist")
    return 1

def send_message(sender, receiver, msg):
    total_info = sender + "\n" + receiver + "\n" + msg
    received_info = send(Operations.SEND_MESSAGE, total_info)
    status = deserialize(received_info)["operation"]
    if status == "00":
        return 0
    print("Message send failure, receiving account does not exist")
    return 1

def view_msgs(username):
    received_info = send(Operations.VIEW_UNDELIVERED_MESSAGES, username)
    status = deserialize(received_info)["operation"]
    if status == "04":
        return deserialize(received_info)["info"]
    print("Cannot retrieve messages")
    return 1

def load_user_menu():
  actions = ["Send messages", "View my messages", "Logout", "Delete account"]
  message = "\nMy Account\n\n"
  user_choice = curses.wrapper(menu, actions, message)

  if user_choice == "Send messages":
    print("\nInput a message and press enter to share, or type STOP to end the chat.\n")
    status = 1
    while status == 1:
      receiver = input("Who would you like to send a message to? ")
      message = input("Message: ")
      if message == "STOP":
        print(f"\n[ENDING CHAT] Ending chat with {SERVER}\n")
        send(Operations.SEND_MESSAGE, DISCONNECT_MESSAGE)
        break
      status = send_message(CURRENT_USER[0], receiver, message)
    load_user_menu()
    return

  elif user_choice == "View my messages": # TODO
    pass
  elif user_choice == "Logout":
    CURRENT_USER[0] = ""
    start()
  elif user_choice == "Delete account":
    status = 1
    while status == 1:
      status = delete_account(CURRENT_USER[0])
    load_user_menu()

def start():
  
  # start menu, lets user pick their first action
  actions = ["Login", "Create account", "List accounts"]
  message = "\nWelcome to Messenger! What would you like to do?\n\n"
  name = curses.wrapper(menu, actions, message)

  if name == "Create account":
    print("\nWelcome to messenger! Please input a username to join.\n")
    status = 1
    while status == 1:
      account_name = input("Username: ")
      if len(account_name) > 10:
        print("\nUsernames must be at most 10 characters.\n")
      else:
        status = create_account(account_name)
    load_user_menu()

  elif name == "Login": 
    status = 1
    while status == 1:
      account_name = input("Username: ")
      status = login(account_name)
    # user menu, lets logged-in user pick what they'd like to do
    load_user_menu()

  elif name == "List accounts": # TODO
    print("TODO")

start()
