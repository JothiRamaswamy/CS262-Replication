import logging
import signal
import socket
import curses
import threading
import time

from menu import menu
from operations import Operations
from protocols import serialize, deserialize

class WireClient:

    PORT = 5050 # port to connect to the server with
    HEADER = 64 # used in getting message size
    FORMAT = "utf-8" # encoding and decoding format
    DISCONNECT_MESSAGE = "!DISCONNECT"
    SERVER_NAME = socket.gethostname() # gets name representing computer on the network
    SERVER = "10.250.39.196" # gets host IPv4 address
    ADDR = (SERVER, PORT) # address that the server is listening into
    SESSION_INFO = {"username": "", "background_listen": True}
    CLIENT_LOCK = threading.Lock() # dealing with thread safety in functions accessing shared resources
    RECEIVE_EVENT = threading.Event() # event for controlling the background thread listening loop
    VERSION = "1"

    CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # connect to server

    def login(self, username):
        """
        Attempts to log the user into the server with the given username.

        Args:
            username (str): The username to use for logging in.

        Returns:
            int: 0 if login was successful, 1 if the account does not exist.
        """
        # send server request to login with username and process response from there
        received_login_info = self.send(Operations.LOGIN, username)
        status = received_login_info["operation"]
        if status == Operations.SUCCESS:
            self.SESSION_INFO["username"] = username
            return 0
        elif status == Operations.ACCOUNT_DOES_NOT_EXIST:
            print("\nThe username you entered does not exist on the server. Please try again or input EXIT to exit.\n")
            return 1

    def create_account(self, username):
        """
        Attempts to create a new account with the given username.

        Args:
            username (str): The username to use for the new account.

        Returns:
            int: 0 if account creation was successful, 1 if the account already exists.
        """
        # send server request to create account with username and process response from there
        received_info = self.send(Operations.CREATE_ACCOUNT, username)
        status = received_info["operation"]
        if status == Operations.SUCCESS:
            self.SESSION_INFO["username"] = username
            return 0
        print("\nThe username you entered already exists on the server. Please try again or input EXIT to exit.\n")
        return 1

    def delete_account(self, username):
      """
      Attempts to delete the account with the given username.

      Args:
          username (str): The username of the account to delete.

      Returns:
          int: 0 if account deletion was successful, 1 if deletion failed.
      """
        # send server request to delete account with username and process response from there
      received_info = self.send(Operations.DELETE_ACCOUNT, username)
      status = received_info["operation"]
      if status == Operations.SUCCESS:
        self.SESSION_INFO["username"] = ""
        return 0
      print("Deletion failure")
      return 1
    
    def logout(self, username):
        """
        Logs out the user with the given username.

        Args:
            username (str): The username of the user to log out.

        Returns:
            int: 0 if logout was successful, 1 if logout failed.
        """
        # send server request to logout with username and process response from there
        received_info = self.send(Operations.LOGOUT, username)
        status = received_info["operation"]
        if status == Operations.SUCCESS:
            self.SESSION_INFO["username"] = ""
            return 0
        print("Logout failure")
        return 1

    def list_accounts(self):
        """
        Requests a list of all the accounts on the server.

        Returns:
            a dictionary containing a list of accounts if the request was successful, 
            1 if the request failed.
        """
        # send server request to list accounts and process response from there
        received_info = self.send(Operations.LIST_ACCOUNTS, "")
        status = received_info["operation"]
        if status == Operations.SUCCESS:
            return received_info
        return 1

    def send_message(self, sender, receiver, msg):
        """
        Sends a message from the given sender to the given receiver.

        Args:
            sender (str): The username of the sender.
            receiver (str): The username of the receiver.
            msg (str): The message to send.

        Returns:
            int: 0 if message sending was successful, 1 if the receiving account does not exist.
        """
        # turn all the info into a string separated by an enter character
        total_info = sender + "\n" + receiver + "\n" + msg
        received_info = self.send(Operations.SEND_MESSAGE, total_info)
        try:
            status = received_info["operation"]
            if status == Operations.SUCCESS: # this will always succeed based on our menu design
                return 0
            print("Message send failure, receiving account does not exist")
            return 1
        except:
            return 1
    
    def view_msgs(self, username):
        """
        View all undelivered messages for the specified user.

        Args:
            username (str): the username of the recipient of the undelivered messages.

        Returns:
            int: 1 if there are no undelivered messages for the specified user, 0 otherwise.
        """
        # send server request to view messages from username and process response from there
        data = self.send(Operations.VIEW_UNDELIVERED_MESSAGES, username)
        if data["operation"] == Operations.FAILURE:
            print("\n" + self.SESSION_INFO["username"] + "'s account does not have any unread messages.")
            return 1
        messages = data["info"].split("\n")
        print("\nList of " + self.SESSION_INFO["username"] + "'s messages:\n")
        for j, message in enumerate(messages):
            print(str(j + 1) + ". " + str(message))
        return 0

    def quit_messenger(self):
      """
      Quit the messenger application by sending a disconnect message to the server and closing the connection.
      """
      # set background thread event to False to exit polling loop, then just return
      try:
        self.send(Operations.SEND_MESSAGE, self.DISCONNECT_MESSAGE)
        self.RECEIVE_EVENT.clear()
        self.CLIENT.close()
      except:
        return

    def receive_incoming_messages(self):
      """
      Receive incoming messages from the server and return the deserialized message.

      Returns:
          None if there is no incoming message, a dictionary containing the deserialized message otherwise.
      """
      try:
        # send a request to check if there are incoming messages from the client
        msg_length = self.CLIENT.recv(self.HEADER, socket.MSG_DONTWAIT)
        if not len(msg_length): # check whether disconnected from server
          print("[DISCONNECTED] You have been disconnected from the server. (Press Ctrl-C to Exit)")
          self.RECEIVE_EVENT.clear()
          self.CLIENT.close()
          return
        elif int(msg_length.decode(self.FORMAT)): # check if messages exist, then handle
          length = int(msg_length.decode(self.FORMAT))
          deserialized_data = deserialize(self.CLIENT.recv(length))
          if deserialized_data["operation"] == Operations.RECEIVE_CURRENT_MESSAGE:
            return deserialized_data
      except BlockingIOError:
        pass
      except Exception as e:
        logging.exception(e)

    def poll_incoming_messages(self, event):
      """
      Continuously poll for incoming messages from the server and print them to the console.

      Args:
          event (threading.Event): the event object that controls the execution of the thread.
      """
      # while the event to run the while loop is still set to true and not turned off yet,
      # poll receive_incoming_messages for immediate messages to deliver
      while event.is_set():
        try:
          with self.CLIENT_LOCK:
            # call receive_incoming_messages to see if there is a message to print
            if self.SESSION_INFO["background_listen"]:
              message = self.receive_incoming_messages()
              if message:
                print("\r\n{}".format(message["info"]))
          time.sleep(1)
        except Exception as e:
          # deal with any errors as they appear and break
          logging.exception(e)
          break

    def send(self, operation, msg):
      """
      Send a message to the server and receive the response.

      Args:
          operation (str): the operation to be performed.
          msg (str): the message to be sent.

      Returns:
          None if there is no response from the server, a dictionary containing the deserialized response otherwise.
      """
      # get serialized form of message
      serialized_message = serialize({"version": self.VERSION, "operation": operation, "info": msg})
      message_length = len(serialized_message)
      # get send_length
      send_length = str(message_length).encode(self.FORMAT)
      send_length += b" " * (self.HEADER - len(send_length))

      with self.CLIENT_LOCK: # lock thread
        self.SESSION_INFO["background_listen"] = False
      self.CLIENT.send(send_length) # first send length
      self.CLIENT.send(serialized_message) # now send message

      message_length = self.CLIENT.recv(self.HEADER).decode(self.FORMAT) # now we get `message_length` back
      returned_operation = Operations.RECEIVE_CURRENT_MESSAGE
      while returned_operation == Operations.RECEIVE_CURRENT_MESSAGE: # while receiving messages
        if message_length:
          message_length = int(message_length)
        else:
          message_length = 1
        try:
          returned_data = self.CLIENT.recv(message_length) # receive `message_length` bytes
          if len(returned_data): # if message exists
            deserialized_data = deserialize(returned_data) # deserialize data
            recv_version = deserialized_data["version"]
            if recv_version != self.VERSION: # check version
              print("Wire Protocol Versions do not match")
              return
            returned_operation = deserialized_data["operation"]
            if returned_operation == Operations.RECEIVE_CURRENT_MESSAGE: # check operation
              print("\r\n{}".format(deserialized_data["info"])) # if receive message, print message
            else:
              with self.CLIENT_LOCK:
                self.SESSION_INFO["background_listen"] = True
              return deserialized_data
          else:
            return
        except Exception as e:
          print(e)
          return

    def get_login_input(self):
      """
      Prompts the user to choose an account to login to.

      Returns:
          Returns self.login(username) if a user logs in successfully, otherwise returns 1 if there are no accounts on the server.
      """
        # get list of accounts to login to
      received_list = self.list_accounts()
      if received_list != 1: # -1 indicates there are not any accounts on server
        # if accounts exist on the server, allow users to choose one and login
        accounts = received_list["info"].split("\n")
        message = "\nChoose an account:\n\n"
        username = curses.wrapper(menu, accounts, message)
        return self.login(username)
      else:
        # if no accounts exist yet on the server, print out a message and return 1 back to
        # the previous menu
        print("\nThere are currently no accounts on the server.\n")
        input("Press enter to return to the main menu.\n\n")
        return 1

    def background_listener(self):
      """
      Starts a background thread that polls for incoming messages from the server.
      """
      # set the background thread event to true so we can control when it is polling until
      self.RECEIVE_EVENT.set()
      # create and start background thread
      background_thread = threading.Thread(target=self.poll_incoming_messages, args=(self.RECEIVE_EVENT,))
      background_thread.start()