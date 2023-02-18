import logging
import signal
import socket
import curses
from threading import Thread
import threading
import time

from importlib_metadata import sys

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
SESSION_INFO = {"username": "", "background_listen": True, "print": True}
# QUEUED_MESSAGES = queue.Queue()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create socket
client.connect(ADDR)

def receive_incoming_messages():
  try:
    msg_length = client.recv(HEADER, socket.MSG_DONTWAIT)
    if not len(msg_length):
      print("[DISCONNECTED] You have been disconnected from the server.")
      client.close()
    if int(msg_length.decode(FORMAT)):
      length = int(msg_length.decode(FORMAT))
      deserialized_data = deserialize(client.recv(length))
      if deserialized_data["operation"] == Operations.RECEIVE_CURRENT_MESSAGE:
        return deserialized_data
  except BlockingIOError:
    pass
  except Exception as e:
    logging.exception(e)

def poll_incoming_messages():
  while True:
    try:
      if SESSION_INFO["background_listen"]:
        message = receive_incoming_messages()
        if message:
          print("\r[INCOMING MESSAGE]{}".format(message["info"]))
      time.sleep(1)
    except Exception as e:
      logging.exception(e)
      break

def background_listener():
  background_thread = threading.Thread(target=poll_incoming_messages)
  print("Starting background thread...")
  background_thread.start()

# def print_incoming_messages():
#   while SESSION_INFO["print"] and not QUEUED_MESSAGES.empty:
#     print(QUEUED_MESSAGES.get())

def send(operation, msg):
  serialized_message = serialize({"operation": operation, "info": msg})
  message_length = len(serialized_message)
  send_length = str(message_length).encode(FORMAT)
  send_length += b" " * (HEADER - len(send_length))
  SESSION_INFO["background_listen"] = False
  client.send(send_length)
  client.send(serialized_message)
  message_length = client.recv(HEADER).decode(FORMAT)
  returned_operation = Operations.RECEIVE_CURRENT_MESSAGE
  while returned_operation == Operations.RECEIVE_CURRENT_MESSAGE:
    if message_length:
      message_length = int(message_length)
    else:
      message_length = 1
    try:
      returned_data = client.recv(message_length)
      if len(returned_data):
        deserialized_data = deserialize(returned_data)
        returned_operation = deserialized_data["operation"]
        if returned_operation == Operations.RECEIVE_CURRENT_MESSAGE:
          # print("\r[INCOMING MESSAGE]{}".format(deserialized_data["info"]))
          pass
        else:
          SESSION_INFO["background_listen"] = True
          return deserialized_data
      else:
        return
    except Exception as e:
      print(e)
      return

def login():
  received_list = send(Operations.LIST_ACCOUNTS, "")
  if received_list["operation"] == Operations.SUCCESS:
    accounts = received_list["info"].split("\n")
    message = "\nChoose an account:\n\n"
    username = curses.wrapper(menu, accounts, message)
    SESSION_INFO["username"] = username
    received_login_info = send(Operations.LOGIN, username)
    status = received_login_info["operation"]
    if status == "00":
      SESSION_INFO["username"] = username
      return 0
    print("\nThe username you entered already exists on the server. Please try again or input EXIT to exit.\n")
    return 1
  else:
    print("\nThere are currently no accounts on the server.\n")
    input("Press enter to return to the main menu.\n\n")
    return 1

def create_account(username):
  received_info = send(Operations.CREATE_ACCOUNT, username)
  status = received_info["operation"]
  if status == "00":
    SESSION_INFO["username"] = username
    return 0
  print("\nThe username you entered already exists on the server. Please try again or input EXIT to exit.\n")
  return 1

def delete_account(username):
  received_info = send(Operations.DELETE_ACCOUNT, username)
  status = received_info["operation"]
  if status == "00":
    SESSION_INFO["username"] = ""
    return 0
  print("Deletion failure")
  return 1

def logout(username):
  received_info = send(Operations.LOGOUT, username)
  status = received_info["operation"]
  if status == "00":
    SESSION_INFO["username"] = ""
    return 0
  print("Logout failure")
  return 1

def list_accounts():
  received_info = send(Operations.LIST_ACCOUNT, "")
  status = received_info["operation"]
  if status == "03":
    return received_info["info"]
  print("Account information does not exist")
  return 1

def send_message(sender, receiver, msg):
  total_info = sender + "\n" + receiver + "\n" + msg
  received_info = send(Operations.SEND_MESSAGE, total_info)
  try:
    status = received_info["operation"]
    if status == "00":
      return 0
    print(status)
    print("Message send failure, receiving account does not exist")
    return 1
  except:
    return 1

def view_msgs(username):

  data = send(Operations.VIEW_UNDELIVERED_MESSAGES, username)

  if data["operation"] == Operations.FAILURE:
    print("\n" + SESSION_INFO["username"] + "'s account does not have any unread messages.")
  else:
    messages = data["info"].split("\n")
    print("\nList of " + SESSION_INFO["username"] + "'s messages:\n")
    for j, message in enumerate(messages):
      print(str(j + 1) + ". " + str(message))
  input("\nPress enter to return to the main menu.\n\n")

def load_user_menu():

  # user menu, lets users pick from a set of actions

  actions = ["Send messages", "View my messages", "Logout", "Delete account"]
  message = "\n" + SESSION_INFO["username"] + "'s Account\n\n"
  user_choice = curses.wrapper(menu, actions, message)

  if user_choice == "Send messages":

    decoded_data = send(Operations.LIST_ACCOUNTS, "")
    accounts = decoded_data["info"].split("\n")
    message = "\nWho would you like to send messages to?\n\n"

    receiver = curses.wrapper(menu, accounts, message)

    print("\nInput a message and press enter to share with " + receiver + " or EXIT to end the chat.\n")
    while True:
      message = input("Message: ")
      processed_message = "<" + SESSION_INFO["username"] + "> " + message 
      if message == "EXIT":
        print(f"\n[ENDING CHAT] Ending chat with {receiver}\n")
        break
      send_message(SESSION_INFO["username"], receiver, processed_message)
    load_user_menu()
    return

  elif user_choice == "View my messages":
    view_msgs(SESSION_INFO["username"])
    load_user_menu()
  elif user_choice == "Logout":
    logout(SESSION_INFO["username"])
    start()
  elif user_choice == "Delete account":

    actions = ["Go back", "Delete forever"]
    message = "\nAre you sure you would like to delete this account? Any unread messages will be permanently lost.\n\n"
    choice = curses.wrapper(menu, actions, message)

    if choice == "Delete forever":
      delete_account(SESSION_INFO["username"])
      return start()
    else:
      load_user_menu()

def start():
  # start menu, lets user pick their first action
  background_listener()
  actions = ["Login", "Create account", "List accounts", "Quit Messenger"]
  message = "\nWelcome to Messenger! What would you like to do?\n\n"
  name = curses.wrapper(menu, actions, message)

  if name == "Quit Messenger":
    send(Operations.SEND_MESSAGE, DISCONNECT_MESSAGE)
    return

  elif name == "Create account":
    print("\nWelcome to messenger! Please input a username to join or EXIT to exit.\n")
    status = 1
    while status == 1:
      account_name = input("Username: ")

      if account_name == "EXIT":
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
    decoded_data = send(Operations.LIST_ACCOUNTS, "")
    if decoded_data["operation"] == Operations.SUCCESS:
      accounts = decoded_data["info"].split("\n")
      print("\nList of accounts currently on the server:\n")
      for j, account in enumerate(accounts):
        print(str(j + 1) + ". " + str(account))
      input("\nPress enter to return to the main menu.\n\n")
    else:
      print("\nThere are currently no accounts on the server.\n")
      input("Press enter to return to the main menu.\n\n")
    
    return start()

def signal_handler(sig, frame):
  send(Operations.SEND_MESSAGE, DISCONNECT_MESSAGE)
  client.close()
  sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

start()