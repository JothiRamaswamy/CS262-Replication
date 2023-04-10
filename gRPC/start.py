import curses
import fnmatch
import os
import sqlite3
import sys
from typing import List
from chat_pb2_grpc import ChatServiceStub
from client import Client
from server import ChatService
from menu import menu
import grpc
import chat_pb2_grpc
from concurrent import futures

def load_user_menu(this_client: Client, stubs: List[ChatServiceStub]):
  """
  Load the user menu for when the client is logged into an account

  Args:
      - this_client: The current instance of Client.
      - stubs (List[ChatServiceStub]): A list of gRPC stubs for the chat server.

  Returns:
      - None
  """
  # Clear terminal for nicer interface dealing with inputs
  os.system('clear')

  ### UI and Menu implementation
  # user menu, lets users pick from a set of actions once they are logged in
  actions = ["Send messages", "View my messages", "Logout", "Delete account"]
  message = "\n" + this_client.SESSION_INFO["username"] + "'s Account\n\n"
  # create curses menu UI from the above parameters
  user_choice = wrap_menu(this_client, menu, actions, message)

  if user_choice == "Send messages":

    # if the user opts to send a message, get the list of accounts to send a message to
    decoded_data = this_client.list_accounts(stubs)
    try:
      accounts = decoded_data.info.split("\n")
    except:
      print("Disconnected from all servers")
      return
    message = "\nWho would you like to send messages to?\n\n"

    # create a menu with possible message receivers
    receiver = wrap_menu(this_client, menu, accounts, message)

    # Instructions for sending messages and exiting the message sending interface
    print("\nInput a message and press enter to share with " + receiver + " or EXIT to end the chat.\n")
    
    # until the user opts to exit message sending interface, keep looping and getting user inputs
    while True:
      message = wrap_input(this_client, "")
      if not message:
          return
      processed_message = "<MESSAGE FROM " + this_client.SESSION_INFO["username"] + "> " + message

      # if the user opts to exit, print a message and break from the loop, leaving the chat
      if message == "EXIT":
        print(f"\n[ENDING CHAT] Ending chat with {receiver}\n")
        break

      # each time a message is inputted, process and send it across the server
      this_client.send_message(this_client.SESSION_INFO["username"], receiver, processed_message, stubs)
    
    # return back to the user menu once exited
    load_user_menu(this_client, stubs)
    return

# if user opts to view undelivered messages, request messages from the server and 
# display them if they are there
  elif user_choice == "View my messages":
    this_client.view_msgs(this_client.SESSION_INFO["username"], stubs)
    wrap_input(this_client, "\nPress enter to return to the main menu.\n\n")
    load_user_menu(this_client, stubs)

# if user opts to logout, process logout and go to start menu
  elif user_choice == "Logout":
    this_client.SESSION_INFO["username"] = ""
    start(this_client, stubs)

  elif user_choice == "Delete account":

    # if user opts to delete account, show a menu confirming their decision
    actions = ["Go back", "Delete forever"]
    message = "\nAre you sure you would like to delete this account? Any unread messages will be permanently lost.\n\n"
    choice = wrap_menu(this_client, menu, actions, message)

    # if the decision is confirmed, process delete request and go to start menu
    if choice == "Delete forever":
      this_client.delete_account(this_client.SESSION_INFO["username"], stubs)
      return start(this_client, stubs)
    else:
      # if they don't confirm the decision, go back to the logged in user menu
      load_user_menu(this_client, stubs)

def start(this_client: Client, stubs: List[ChatServiceStub]):
  """
  Load the start menu for when the client enters the service or is not logged in

  Args:
      - this_client: The current instance of Client.
      - stubs (List[ChatServiceStub]): A list of gRPC stubs for the chat server.

  Returns:
      - None
  """
  # Clear terminal for nicer interface dealing with inputs
  os.system('clear')
  
  ### UI and Menu implementation
  # start menu, lets user pick their first action before logging in/creating acct
  actions = ["Login", "Create account", "List accounts", "Quit Messenger"]
  message = "\nWelcome to Messenger! What would you like to do?\n\n"
  try:
    # create menu with above actions and message
    name = wrap_menu(this_client, menu, actions, message)
  except KeyboardInterrupt:
    return this_client.quit_messenger()

  # if user opts to quit messenger, quit and exit the chat service
  if name == "Quit Messenger" or name == 0:
    return this_client.quit_messenger()

  # if user opts to create an account, prompt user for an input and validate that it isn't used
  elif name == "Create account":
    print("\nWelcome to messenger! Please input a username to join or EXIT to exit.\n")
    status = 1
    while status == 1:
      account_name = wrap_input(this_client, "Username: ")

      if not account_name:
          return

      # if the user tries to exit the input interface, go back to start menu beginning
      if account_name == "EXIT":
        return start(this_client, stubs)

      if len(account_name) > 10:
        print("\nUsernames must be at most 10 characters.\n")
      else:
        # if length of username works, validate that it isn't already used. Otherwise, stay in loop
        status = this_client.create_account(account_name, stubs)
    
    # if valid username, direct the now logged in user to user menu
    load_user_menu(this_client, stubs)

  # if the user opts to login, get their login input and validate that the username exists.
  # if login successful direct to user menu, otherwise go back to start menu
  elif name == "Login":
    try:
        if this_client.get_login_input(stubs) == 0:
            load_user_menu(this_client, stubs)
        elif this_client.get_login_input(stubs) == -1:
            print("Disconnected from all servers")
            return
        else:
            return start(this_client, stubs)
    except KeyboardInterrupt:
        return this_client.quit_messenger()

# if the user opts to list existing accounts, get the list of accounts from the server
  elif name == "List accounts":
    decoded_data = this_client.list_accounts(stubs)
    if decoded_data != 1:
      # if the list is valid, split it by the enter character that initially divided it
      accounts = decoded_data.info.split("\n")
      # request a text wildcard to search the list of accounts
      print("\nPlease input a text wildcard. * matches everything, ? matches any single character, [seq] matches any character in seq, and [!seq] matches any character not in seq.\n")
      wildcard = wrap_input(this_client, "Text wildcard: ")
      if not wildcard:
          return
      
      # if the wildcard is valid, filter the list of accounts based on this and return them
      print("\nList of accounts currently on the server matching " + wildcard + ":\n")
      for account in accounts:
        if fnmatch.fnmatch(account, wildcard):
          print(str(account))
      wrap_input(this_client, "\nPress enter to return to the main menu.\n\n")
    
    # if no accounts exist on the server, print the error and allow the user to go back to the start menu
    else:
      print("\nThere are currently no accounts on the server.\n")
      wrap_input(this_client, "Press enter to return to the main menu.\n\n")
    
    return start(this_client, stubs)

def wrap_menu(this_client, menu, actions, message):
    """
    Wraps a curses menu function so we can exit it with ctrl-C.

    Args:
        this_client: The client running the menu.
        menu: The menu function to be wrapped.
        actions: A list of actions available in the menu.
        message: A message to be displayed when the menu is shown.

    Returns:
        The result of calling the curses menu function.

    Raises:
        KeyboardInterrupt: If the user presses Ctrl-C while the menu is being displayed.
    """
    try:
        return curses.wrapper(menu, actions, message)
    except KeyboardInterrupt:
        return this_client.quit_messenger()

def wrap_input(this_client, string):
    """
    Wraps the input() function so we can exit it with ctrl-C.

    Args:
        this_client: The instance of the Client class calling input().
        string: The prompt to display to the user.

    Returns:
        The user's input.

    Raises:
        KeyboardInterrupt: If the user presses Ctrl-C while the prompt is being displayed.
    """
    try:
        return input(string)
    except KeyboardInterrupt:
        return this_client.quit_messenger()


if __name__ == "__main__":

  SERVER_HOST = "localhost:3001"
  SERVER_HOST_BACKUP_1 = "localhost:3002"
  SERVER_HOST_BACKUP_2 = "localhost:3003"

  if len(sys.argv) < 2:
    print("please specify running client or server")

# if the client is specified as what the user wants to start, connect grpc to server host, create
# client, start background listener thread, and direct to start menu 
  elif sys.argv[1] == "client":
    os.system('clear') # clear terminal on start for client
    with grpc.insecure_channel(SERVER_HOST) as channel:
      with grpc.insecure_channel(SERVER_HOST_BACKUP_1) as channel1:
        with grpc.insecure_channel(SERVER_HOST_BACKUP_2) as channel2: # channel to connect grpc, make calls
          stub = chat_pb2_grpc.ChatServiceStub(channel)
          stub1 = chat_pb2_grpc.ChatServiceStub(channel1)
          stub2 = chat_pb2_grpc.ChatServiceStub(channel2)
          client = Client()

          start(client, [stub, stub1, stub2])


# if the server is specified as what the user wants to start, connect grpc server, create server
# object, and start it
  elif sys.argv[1] == "server":
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), options=(('grpc.so_reuseport', 0),))
    HOST = SERVER_HOST
    db = "user_database"
    try:
      server.add_insecure_port(SERVER_HOST)
    except RuntimeError:
      try:
        HOST = SERVER_HOST_BACKUP_1
        db = "user_database_2"
        server.add_insecure_port(SERVER_HOST_BACKUP_1)
      except RuntimeError:
        HOST = SERVER_HOST_BACKUP_2
        db = "user_database_3"
        server.add_insecure_port(SERVER_HOST_BACKUP_2)
    service = ChatService()
    service.start_db(db)
    chat_pb2_grpc.add_ChatServiceServicer_to_server(service, server)
    os.system('clear')
    print("[STARTING] Server is starting at IPv4 Address " + HOST + " ...")
    conn = sqlite3.connect(db, check_same_thread=False) 
    c = conn.cursor()
    c.execute('''
          CREATE TABLE IF NOT EXISTS users
          ([user_id] INTEGER PRIMARY KEY, [user_name] TEXT, [incoming_messages] TEXT)
          ''')
    server.start()
    server.wait_for_termination()

  else:
    print("please specify running client or server")