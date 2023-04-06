# inspired by grpc helloworld tutorial at https://github.com/grpc/grpc/tree/master/examples/python/helloworld
import threading

import chat_pb2
import chat_pb2_grpc
from user import User

import sqlite3
import numpy as np


class ChatService(chat_pb2_grpc.ChatServiceServicer):

    PORT = 5050 # port to connect to the server with
    SERVER_HOST = '10.250.35.25' # gets host IPv4 address
    ADDR = (SERVER_HOST, PORT) # address that the server is listening into
    SEPARATE_CHARACTER = "\n" # character to concat lists into strings with

    USER_LOCK = threading.Lock() # dealing with thread safety in functions accessing shared resources

    USERS = {} # dictionary holding all user objects { key: username, value: user object}

    LISTEN_FLAG = True

    conn = sqlite3.connect('user_database', check_same_thread=False) 
    c = conn.cursor()

    def is_valid_user(self, username: str):
        self.c.execute('''
            SELECT
            user_name
            FROM users
            ''')
        users = np.array(self.c.fetchall()).flatten()
        return username in users

    def LoginClient(self, request, context):
        """
        A method that handles a client's login request. Separated from processing for ease 
        of testing
        """
        return self.login_processing(request)

    def CreateAccountClient(self, request, context):
        """
        A method that handles a client's create account request. Separated from processing for ease 
        of testing
        """
        return self.create_account_processing(request)

    def DeleteAccountClient(self, request, context):
        """
        A method that handles a client's delete account request. Separated from processing for ease 
        of testing
        """
        return self.delete_account_processing(request)

    def ListAccountClient(self, request, context):
        """
        A method that handles a client's list account request. Separated from processing for ease 
        of testing
        """
        return self.list_account_processing()

    def SendMessageClient(self, request, context):
        """
        A method that handles a client's send message request. Separated from processing for ease 
        of testing
        """
        return self.send_msg_processing(request)

    def ViewMessageClient(self, request, context):
        """
        A method that handles a client's view message request. Separated from processing for ease 
        of testing
        """
        return self.view_msg_processing(request)

    def LogoutClient(self, request, context):
        """
        A method that handles a client's logout request. Separated from processing for ease 
        of testing
        """
        return self.logout_processing(request)

    def CheckIncomingMessagesClient(self, request, context):
        """
        A method that handles a client's request for immediate messages. Separated from processing 
        for ease of testing
        """
        if self.LISTEN_FLAG:
            return self.check_msg_processing(request)

    def login_processing(self, request):
        """Attempts to process a client's login request.

        Args:
            request (ClientMessage): The username to log in with.

        Returns:
            ServerMessage: status SUCCESS if the login attempt was successful, ACCOUNT_DOES_NOT_EXIST
            if the account does not exist on the server.
        """
        # if the requested username is in the existing users, log the user in and return success
        with self.USER_LOCK:
            if self.is_valid_user(request.info):
                return chat_pb2.ServerMessage(operation=chat_pb2.SUCCESS, info="")
        # if the requested username is not associated with a current user, return ACCOUNT_DOES_NOT_EXIST
        return chat_pb2.ServerMessage(operation=chat_pb2.ACCOUNT_DOES_NOT_EXIST, info="")

    def create_account_processing(self, request):
        """Attempts to process a client's create account request.

        Args:
            request (ClientMessage): The username to create account with.

        Returns:
            ServerMessage: status SUCCESS if the create attempt was successful, ACCOUNT_ALREADY_EXISTS
            if the account already exists on the server.
        """
        # if the requested username is in the existing users, log the user in and return ACCOUNT_ALREADY_EXISTS
        with self.USER_LOCK:
            if self.is_valid_user(request.info):
                return chat_pb2.ServerMessage(operation=chat_pb2.ACCOUNT_ALREADY_EXISTS, info="")
            new_user = User(request.info)
            self.USERS[request.info] = new_user
            self.c.execute('''
          INSERT INTO users (user_name, incoming_messages)

                VALUES
                (?, ?)
          ''', (request.info, ''))
            self.conn.commit()
        # if the requested username is not associated with a current user, return success
        return chat_pb2.ServerMessage(operation=chat_pb2.SUCCESS, info="")

    def delete_account_processing(self, request):
        """Attempts to process a client's delete account request.

        Args:
            request (ClientMessage): The username to delete account for.

        Returns:
            ServerMessage: status SUCCESS if the delete attempt was successful, ACCOUNT_DOES_NOT_EXIST
            if the account does not exist on the server.
        """
        with self.USER_LOCK:
            # if the requested username is in the existing users and logged in, delete and return success
            if self.is_valid_user(request.info):
                execute_str = 'DELETE FROM users WHERE user_name = \'' + request.info + '\''
                self.c.execute(execute_str)
                self.conn.commit()
                return chat_pb2.ServerMessage(operation=chat_pb2.SUCCESS, info="")
        # if the requested username is not associated with a current user, return ACCOUNT_DOES_NOT_EXIST
        return chat_pb2.ServerMessage(operation=chat_pb2.ACCOUNT_DOES_NOT_EXIST, info="")

    def list_account_processing(self):
        """Attempts to process a client's list account request.

        Returns:
            ServerMessage: status SUCCESS if the list attempt was successful, FAILURE if no accounts
            exist on the server.
        """
        with self.USER_LOCK:
            # otherwise, get the usernames of existing users, concat them, and send back to client
            self.c.execute('SELECT user_name FROM users')
            accounts = np.array(self.c.fetchall()).flatten()
            accounts_string = "\n".join(accounts).strip()
            return chat_pb2.ServerMessage(operation=chat_pb2.SUCCESS, info=accounts_string)

    def send_msg_processing(self, request):
        """Attempts to process a client's send message request.

        Args:
            request (ClientMessage): The info on sender, receiver, message to process

        Returns:
            ServerMessage: status SUCCESS if the send attempt was successful, FAILURE otherwise.
        """
        # extract sender, receiver, and message from request info
        sender, receiver, msg = request.info.split("\n")
        with self.USER_LOCK:
            # if the sender and receiver are valid users, queue the message based on the logged in
            # status of the receiver
            if self.is_valid_user(receiver):
                self.LISTEN_FLAG = False
                self.c.execute('SELECT incoming_messages FROM users WHERE user_name =?', (receiver,))
                messages = np.array(self.c.fetchall()).flatten()[0].strip()
                if len(messages) > 0:
                    messages += "\n" + msg
                else:
                    messages = msg
                execute_str = 'UPDATE users SET incoming_messages = \'' + messages + "\' WHERE user_name = \'" + receiver + "\'"
                self.c.execute(execute_str)
                self.conn.commit()
                self.LISTEN_FLAG = True
                return chat_pb2.ServerMessage(operation=chat_pb2.SUCCESS, info="")
            else:
                return chat_pb2.ServerMessage(operation=chat_pb2.FAILURE, info="")

    def view_msg_processing(self, request):
        """Attempts to process a client's view undelivered messages request.

        Args:
            request (ClientMessage): The username to view messages for

        Returns:
            ServerMessage: status NO_MESSAGES if none exist, MESSAGES_EXIST if they do, FAILURE if 
            user is invalid.
        """
        with self.USER_LOCK:
            # if the request user is valid, show undelivered messages if the queue is not empty
            if self.is_valid_user(request.info):
                self.c.execute('SELECT incoming_messages FROM users WHERE user_name=?', (request.info, ))
                message_str = np.array(self.c.fetchall()).flatten()[0]
                if len(message_str) == 0: # handle case of no undelivered messages
                    return chat_pb2.ServerMessage(operation=chat_pb2.NO_MESSAGES, info="")
                # join messages and send back to client
                execute_str = 'UPDATE users SET incoming_messages = "" WHERE user_name = \'' + request.info + '\''
                self.c.execute(execute_str)
                self.conn.commit()
                return chat_pb2.ServerMessage(operation=chat_pb2.MESSAGES_EXIST, info=message_str)
            return chat_pb2.ServerMessage(operation=chat_pb2.FAILURE, info="")

    def logout_processing(self, request):
        """Attempts to process a client's logout request.

        Args:
            request (ClientMessage): The username to logout

        Returns:
            ServerMessage: status SUCCESS if successfully logged out, FAILURE otherwise.
        """
        pass

    def check_msg_processing(self, request):
        """Attempts to process a client's request to check for messages to deliver immediately.

        Args:
            request (ClientMessage): The username to check messages for

        Returns:
            ServerMessage: status NO_MESSAGES if none exist, MESSAGES_EXIST if they do, FAILURE if 
            user is invalid.
        """
        return self.view_msg_processing(request)
        
