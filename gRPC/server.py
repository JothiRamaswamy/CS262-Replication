import threading
import chat_pb2
import chat_pb2_grpc
from user import User
import sqlite3
import numpy as np


class ChatService(chat_pb2_grpc.ChatServiceServicer):
    SEPARATE_CHARACTER = "\n"

    USER_LOCK = threading.Lock()

    LISTEN_FLAG = True

    def start_db(self, db):
        self.conn = sqlite3.connect(db, check_same_thread=False)
        self.c = self.conn.cursor()


    def is_valid_user(self, username: str):
        self.c.execute(
            """
            SELECT
            user_name
            FROM users
            """
        )
        users = np.array(self.c.fetchall()).flatten()
        return username in users

    def LoginClient(self, request, context):
        return self.login_processing(request)

    def CreateAccountClient(self, request, context):
        return self.create_account_processing(request)

    def DeleteAccountClient(self, request, context):
        return self.delete_account_processing(request)

    def ListAccountClient(self, request, context):
        return self.list_account_processing()

    def SendMessageClient(self, request, context):
        return self.send_msg_processing(request)

    def ViewMessageClient(self, request, context):
        return self.view_msg_processing(request)

    def LogoutClient(self, request, context):
        return self.logout_processing(request)

    def CheckIncomingMessagesClient(self, request, context):
        if self.LISTEN_FLAG:
            return self.check_msg_processing(request)

    def login_processing(self, request):
        with self.USER_LOCK:
            if self.is_valid_user(request.info):
                return chat_pb2.ServerMessage(operation=chat_pb2.SUCCESS, info="")

        return chat_pb2.ServerMessage(
            operation=chat_pb2.ACCOUNT_DOES_NOT_EXIST, info=""
        )

    def create_account_processing(self, request):
        with self.USER_LOCK:
            if self.is_valid_user(request.info):
                return chat_pb2.ServerMessage(
                    operation=chat_pb2.ACCOUNT_ALREADY_EXISTS, info=""
                )
            self.c.execute(
                """
          INSERT INTO users (user_name, incoming_messages)

                VALUES
                (?, ?)
          """,
                (request.info, ""),
            )
            self.conn.commit()

        return chat_pb2.ServerMessage(operation=chat_pb2.SUCCESS, info="")

    def delete_account_processing(self, request):
        with self.USER_LOCK:
            if self.is_valid_user(request.info):
                # Use parameterized query instead of string concatenation
                self.c.execute("DELETE FROM users WHERE user_name = ?", (request.info,))
                self.conn.commit()
                return chat_pb2.ServerMessage(operation=chat_pb2.SUCCESS, info="")
        return chat_pb2.ServerMessage(
            operation=chat_pb2.ACCOUNT_DOES_NOT_EXIST, info=""
        )

    def list_account_processing(self):
        with self.USER_LOCK:
            self.c.execute("SELECT user_name FROM users")
            accounts = np.array(self.c.fetchall()).flatten()
            accounts_string = "\n".join(accounts).strip()
            return chat_pb2.ServerMessage(
                operation=chat_pb2.SUCCESS, info=accounts_string
            )

    def send_msg_processing(self, request):
        sender, receiver, msg = request.info.split("\n")
        with self.USER_LOCK:
            if self.is_valid_user(receiver):
                self.LISTEN_FLAG = False
                self.c.execute(
                    "SELECT incoming_messages FROM users WHERE user_name =?",
                    (receiver,),
                )
                messages = np.array(self.c.fetchall()).flatten()[0].strip()
                if len(messages) > 0:
                    messages += "\n" + msg
                else:
                    messages = msg

                # Use parameterized query instead of string concatenation
                self.c.execute(
                    "UPDATE users SET incoming_messages = ? WHERE user_name = ?",
                    (messages, receiver),
                )
                self.conn.commit()
                self.LISTEN_FLAG = True
                return chat_pb2.ServerMessage(operation=chat_pb2.SUCCESS, info="")
            else:
                return chat_pb2.ServerMessage(operation=chat_pb2.FAILURE, info="")

    def view_msg_processing(self, request):
        with self.USER_LOCK:
            if self.is_valid_user(request.info):
                self.c.execute(
                    "SELECT incoming_messages FROM users WHERE user_name=?",
                    (request.info,),
                )
                message_str = np.array(self.c.fetchall()).flatten()[0]
                if len(message_str) == 0:
                    return chat_pb2.ServerMessage(
                        operation=chat_pb2.NO_MESSAGES, info=""
                    )

                execute_str = (
                    'UPDATE users SET incoming_messages = "" WHERE user_name = \''
                    + request.info
                    + "'"
                )
                self.c.execute(execute_str)
                self.conn.commit()
                return chat_pb2.ServerMessage(
                    operation=chat_pb2.MESSAGES_EXIST, info=message_str
                )
            return chat_pb2.ServerMessage(operation=chat_pb2.FAILURE, info="")

    def logout_processing(self, request):
        pass

    def check_msg_processing(self, request):
        return self.view_msg_processing(request)