import socket
import curses
from time import sleep

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

def login():
    encoded_data = send(Operations.LIST_ACCOUNTS, "")
    decoded_data = deserialize(encoded_data) # get accounts back
    if decoded_data["operation"] == Operations.SUCCESS:
      accounts = decoded_data["info"].split("\n")
      message = "\nChoose an account:\n\n"
      account = curses.wrapper(menu, accounts, message)
      CURRENT_USER[0] = account
      return 0
    else:
      print("\nThere are currently no accounts on the server.\n")
      input("Press enter to return to the main menu.\n\n")
      return 1

def create_account(username):
    received_info = send(Operations.CREATE_ACCOUNT, username)
    status = deserialize(received_info)["operation"]
    if status == "00":
      CURRENT_USER[0] = username
      return 0
    print("\nThe username you entered already exists on the server. Please try again or type STOP to exit.\n")
    return 1

def delete_account(username):
    received_info = send(Operations.DELETE_ACCOUNT, username)
    deserialize(received_info)["operation"]
    CURRENT_USER[0] = ""

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
    print(deserialize(received_info))
    try:
      status = deserialize(received_info)["operation"]
      if status == "00":
          return 0
      print("Message send failure, receiving account does not exist")
      return 1
    except:
      print(deserialize(received_info))
      print("something didn't work...")
      return 1

def view_msgs(username):
    received_info = send(Operations.VIEW_UNDELIVERED_MESSAGES, username)
    data = deserialize(received_info)
    if data["operation"] == "04":
      print(data)
      print(data["info"])
      return 0
    print("Cannot retrieve messages")
    return 1

def load_user_menu():
  actions = ["Send messages", "View my messages", "Logout", "Delete account"]
  message = "\n" + CURRENT_USER[0] + "'s Account\n\n"
  user_choice = curses.wrapper(menu, actions, message)

  if user_choice == "Send messages":
    print("\nInput a message and press enter to share, or type STOP to end the chat.\n")
    status = 1
    while status == 1:
      receiver = input("Who would you like to send a message to? ")
      message = input("Message: ")
      final_message = "<" + CURRENT_USER[0] + "> " + message 
      if message == "STOP":
        print(f"\n[ENDING CHAT] Ending chat with {SERVER}\n")
        send(Operations.SEND_MESSAGE, DISCONNECT_MESSAGE)
        break
      status = send_message(CURRENT_USER[0], receiver, final_message)
    load_user_menu()
    return

  elif user_choice == "View my messages":
    status = view_msgs(CURRENT_USER[0])
    response = input("Back to menu? (Y/n) ")
    if response == "Y":
      load_user_menu()
  elif user_choice == "Logout":
    CURRENT_USER[0] = ""
    return start()
  elif user_choice == "Delete account":
    delete_account(CURRENT_USER[0])
    return start()

def start():
  # start menu, lets user pick their first action
  actions = ["Login", "Create account", "List accounts", "Quit Messenger"]
  message = "\nWelcome to Messenger! What would you like to do?\n\n"
  name = curses.wrapper(menu, actions, message)

  if name == "Quit Messenger":
    return

  elif name == "Create account":
    print("\nWelcome to messenger! Please input a username to join.\n")
    status = 1
    while status == 1:
      account_name = input("Username: ")

      if account_name == "STOP":
        return start()

      if len(account_name) > 10:
        print("\nUsernames must be at most 10 characters.\n")
      else:
        status = create_account(account_name)
    
    load_user_menu()

  elif name == "Login":
    if login() == 0:
      load_user_menu()
    else:
      return start()

  elif name == "List accounts":
    encoded_data = send(Operations.LIST_ACCOUNTS, "")
    decoded_data = deserialize(encoded_data) # get accounts back
    if decoded_data["operation"] == Operations.SUCCESS:
      accounts = decoded_data["info"].split("\n")
      print("\nList of accounts currently on the server:\n")
      for account in accounts:
        print(account)
      input("\nPress enter to return to the main menu.\n\n")
    else:
      print("\nThere are currently no accounts on the server.\n")
      input("Press enter to return to the main menu.\n\n")
    
    return start()

start()