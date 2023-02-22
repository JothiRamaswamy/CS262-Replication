import logging
import socket
import curses
import threading
import time
from chat_pb2 import ServerMessage

from menu import menu

from chat_pb2_grpc import ChatServiceStub

import chat_pb2

class Client:

    PORT = 5050 # port to connect to the server with
    SERVER_NAME = socket.gethostname() # gets name representing computer on the network
    SERVER = socket.gethostbyname(SERVER_NAME) # gets host IPv4 address
    ADDR = (SERVER, PORT) # address that the server is listening into
    SESSION_INFO = {"username": ""} # store who is logged in at the moment
    CLIENT_LOCK = threading.Lock() # dealing with thread safety in functions accessing shared resources
    RECEIVE_EVENT = threading.Event() # event for controlling the background thread listening loop

    def login(self, username, stub: ChatServiceStub):
        """
        Attempts to log in with the specified username.

        Args:
            username (str): The username to log in with.
            stub (ChatServiceStub): A gRPC stub for the chat server.

        Returns:
            int: 0 if the login attempt was successful, 1 if the specified
                username does not exist on the server, or None if there was an
                error.
        """
        # send server request to login with username and process response from there
        received_info = stub.LoginClient(chat_pb2.ClientMessage(info=username))
        return self.login_processing(username, received_info)

    def create_account(self, username, stub: ChatServiceStub):
        """
        Attempts to create a new account with the specified username.

        Args:
            username (str): The username to create the account with.
            stub (ChatServiceStub): A gRPC stub for the chat server.

        Returns:
            int: 0 if the account creation was successful, 1 if the specified
                username already exists on the server, or None if there was an
                error.
        """
        # send server request to create account with username and process response from there
        received_info = stub.CreateAccountClient(chat_pb2.ClientMessage(info=username))
        return self.create_account_processing(username, received_info)

    def delete_account(self, username, stub: ChatServiceStub):
        """
        Attempts to delete the account associated with the specified username.

        Args:
            username (str): The username to delete the account for.
            stub (ChatServiceStub): A gRPC stub for the chat server.

        Returns:
            int: 0 if the account deletion was successful, 1 if there was a
                deletion failure, or None if there was an error.
        """
        # send server request to delete account with username and process response from there
        received_info = stub.DeleteAccountClient(chat_pb2.ClientMessage(info=username))
        return self.delete_account_processing(username, received_info)
    
    def logout(self, username, stub: ChatServiceStub):
        """
        Attempts to log out of the account associated with the specified username.

        Args:
            username (str): The username to log out of.
            stub (ChatServiceStub): A gRPC stub for the chat server.

        Returns:
            int: 0 if the logout was successful, 1 if there was a logout failure,
                or None if there was an error.
        """
        # send server request to logout with username and process response from there
        received_info = stub.LogoutClient(chat_pb2.ClientMessage(info=username))
        return self.logout_processing(username, received_info)

    def list_accounts(self, stub: ChatServiceStub):
        """
        Attempts to list all of the accounts created in the chat server.

        Args:
            stub (ChatServiceStub): A gRPC stub for the chat server.

        Returns:
            int: a string of joined usernames if successful, 1 if there was an error.
        """
        # send server request to list accounts and process response from there
        received_info = stub.ListAccountClient(chat_pb2.ClientMessage(info=""))
        return self.list_account_processing(received_info)

    def send_message(self, sender, receiver, msg, stub: ChatServiceStub):
        """
        Attempts to send a message from a sender account to a receiver account.

        Args:
            sender (str): The username of the account sending the message.
            receiver (str): The username of the account receiving the message.
            message (str): The message to send from sender to receiver.
            stub (ChatServiceStub): A gRPC stub for the chat server.

        Returns:
            int: 0 if the send was successful, 1 if there was a send failure.
        """
        # turn all the info into a string separated by an enter character
        total_info = sender + "\n" + receiver + "\n" + msg
        # send server request to send message to receiver and process response from there
        received_info = stub.SendMessageClient(chat_pb2.ClientMessage(info=total_info))
        return self.send_message_processing(received_info)
    
    def view_msgs(self, username, stub: ChatServiceStub):
        """
        Attempts to retrieve all unread messages for the specified user.

        Args:
            username (str): The username of the user whose messages will be retrieved.
            stub (ChatServiceStub): A gRPC stub for the chat server.

        Returns:
            int: 0 if the operation was successful, 1 if there was a failure.
        """
        # send server request to view messages from username and process response from there
        received_info = stub.ViewMessageClient(chat_pb2.ClientMessage(info=username))
        return self.view_message_processing(received_info)

    def login_processing(self, username, received_info: ServerMessage):
        """
        Processes login status received from server and returns an integer.

        Args:
        - username: a string representing the username to be logged in
        - received_info: an instance of ServerMessage representing the response from the server

        Returns:
        - 0 if login is successful, 1 otherwise
        """
        # get status of the server response
        status = received_info.operation
        # if the status is successful, update the session info with the logged in user and return 0
        if status == chat_pb2.SUCCESS:
            self.SESSION_INFO["username"] = username
            return 0
        # if a user with a nonexistent acct tries to log in, print an error and return 1
        elif status == chat_pb2.ACCOUNT_DOES_NOT_EXIST:
            print("\nThe username you entered does not exist on the server. Please try again or input EXIT to exit.\n")
            return 1

    def create_account_processing(self, username, received_info: ServerMessage):
        """
        Processes account creation status received from server and returns an integer.

        Args:
        - username: a string representing the username to be created
        - received_info: an instance of ServerMessage representing the response from the server

        Returns:
        - 0 if create is successful, 1 otherwise
        """
        # get status of the server response
        status = received_info.operation
        # if the status is successful, update the session info with the logged in user and return 0
        if status == chat_pb2.SUCCESS:
            self.SESSION_INFO["username"] = username
            return 0
        # if a user tries to create an acct with an existing username, print an error and return 1
        print("\nThe username you entered already exists on the server. Please try again or input EXIT to exit.\n")
        return 1

    def delete_account_processing(self, username, received_info: ServerMessage):
        """
        Processes account deletion status received from server and returns an integer.

        Args:
        - username: a string representing the username to be deleted
        - received_info: an instance of ServerMessage representing the response from the server

        Returns:
        - 0 if deletion is successful, 1 otherwise
        """
        # get status of the server response
        status = received_info.operation
        # if the status is successful, reset the session info and return 0
        if status == chat_pb2.SUCCESS:
            self.SESSION_INFO["username"] = ""
            return 0
        # if the deletion didn't work, print an error and return 1
        print("Deletion failure")
        return 1

    def logout_processing(self, username, received_info: ServerMessage):
        """
        Processes logout status received from server and returns an integer.

        Args:
        - username: a string representing the username to be logged out
        - received_info: an instance of ServerMessage representing the response from the server

        Returns:
        - 0 if logout is successful, 1 otherwise
        """
        # get status of the server response
        status = received_info.operation
        # if the status is successful, reset the session info and return 0
        if status == chat_pb2.SUCCESS:
            self.SESSION_INFO["username"] = ""
            return 0
        # if the logout didn't work, print an error and return 1
        print("Logout failure")
        return 1

    def list_account_processing(self, received_info: ServerMessage):
        """
        Processes list of accounts received from server and returns either a ServerMessage instance or an integer.

        Args:
        - received_info: an instance of ServerMessage representing the response from the server

        Returns:
        - ServerMessage instance containing the list of accounts if successful, 1 otherwise
        """
        # get status of the server response
        status = received_info.operation
        # if the status is successful, return the stringified list of accounts
        if status == chat_pb2.SUCCESS:
            return received_info
        # if there are no accounts, print an error and return 1
        print("Account information does not exist")
        return 1

    def send_message_processing(self, received_info: ServerMessage):
        """
        Process the received information of sending a message.

        Args:
        - received_info: an instance of ServerMessage representing the response from the server

        Returns:
        - 0 if message sending is successful, 1 otherwise
        """
        # get status of the server response
        status = received_info.operation
        # if the status is successful, return the stringified list of accounts
        if status == chat_pb2.SUCCESS:
            return 0
        # if the message send didn't work, print an error and return 1
        print("Message send failure, receiving account does not exist")
        return 1

    def view_message_processing(self, received_info: ServerMessage):
        """
        Process the received information of viewing undelivered messages.

        Args:
        - received_info: an instance of ServerMessage representing the response from the server

        Returns:
        - 0 if message viewing is successful, 1 otherwise
        """
        # if the server request status is FAILURE, print out that there are no unread msgs and return 1
        if received_info.operation == chat_pb2.FAILURE:
            print("\n" + self.SESSION_INFO["username"] + "'s account does not have any unread messages.")
            return 1
        # otherwise print out the unread messages in a numbered list, split by the enter character
        messages = received_info.info.split("\n")
        print("\nList of " + self.SESSION_INFO["username"] + "'s messages:\n")
        for j, message in enumerate(messages):
            print(str(j + 1) + ". " + str(message))
        # once this is done successfully, return 0
        return 0

    def quit_messenger(self):
        """
        Quit the messenger.

        Returns: None
        """
        # set background thread event to False to exit polling loop, then just return
        self.RECEIVE_EVENT.clear()
        return


    def receive_incoming_messages(self, username, stub: ChatServiceStub):
        """
        Receive incoming messages from the server, polled in background thread.

        Args:
        - username: string representing the client's username
        - stub (ChatServiceStub): A gRPC stub for the chat server.

        Returns:
        - -1 if an interruption occurs during message receiving, None otherwise
        """
        try:
            # send a request to check if there are incoming messages from the client
            receive_info = stub.CheckIncomingMessagesClient(chat_pb2.ClientMessage(info=username))
            # if messages exist, print them
            if receive_info.operation == chat_pb2.MESSAGES_EXIST:
                for message in receive_info.info.split("\n"):
                    print("\r" + message)
        except KeyboardInterrupt:
            # deal with Ctrl-C in the background thread
            return -1
        except Exception as e:
            # deal with any errors as they appear
            logging.exception(e)

    def poll_incoming_messages(self, event, stub: ChatServiceStub):
        """
        Poll incoming messages from the server in background thread to deliver on demand.

        Args:
        - event (Threading.Event()): the flag to signal when to stop the thread
        - stub (ChatServiceStub): A gRPC stub for the chat server.

        Returns: None
        """
        # while the event to run the while loop is still set to true and not turned off yet,
        # poll receive_incoming_messages for immediate messages to deliver
        while event.is_set():
            # don't do anything if no one is logged in
            if self.SESSION_INFO["username"] == "":
                continue
            try:
                with self.CLIENT_LOCK:
                    # call receive_incoming_messages to see if there is a message to print
                    message = self.receive_incoming_messages(self.SESSION_INFO["username"], stub)
                    # if ctrl-c was hit, break
                    if message and message == -1:
                        break
                time.sleep(1)
            except Exception as e:
                # deal with any errors as they appear and break
                logging.exception(e)
                break

    def get_login_input(self, stub: ChatServiceStub):
        """
        Displays a list of accounts to log in to and allows the user to choose one to log in.
        
        Args:
        - stub (ChatServiceStub): A gRPC stub for the chat server.

        Returns: login status if accounts exist to log into, 1 otherwise
        """
        # get list of accounts to login to
        received_list = self.list_accounts(stub)
        if received_list != 1:
            # if accounts exist on the server, allow users to choose one and login
            accounts = received_list.info.split("\n")
            message = "\nChoose an account:\n\n"
            username = curses.wrapper(menu, accounts, message)
            return self.login(username, stub)
        else:
            # if no accounts exist yet on the server, print out a message and return 1 back to
            # the previous menu
            print("\nThere are currently no accounts on the server.\n")
            input("Press enter to return to the main menu.\n\n")
            return 1

    def background_listener(self, stub: ChatServiceStub):
        """
        Starts a background thread to poll for incoming messages.
        
        Args:
        - stub (ChatServiceStub): A gRPC stub for the chat server.

        Returns: None
        """
        # set the background thread event to true so we can control when it is polling until
        self.RECEIVE_EVENT.set()
        # create and start background thread
        background_thread = threading.Thread(target=self.poll_incoming_messages, args=(self.RECEIVE_EVENT,stub))
        background_thread.start()