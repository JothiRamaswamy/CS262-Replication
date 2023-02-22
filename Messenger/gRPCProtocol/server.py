# Copyright 2015 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Python implementation of the GRPC helloworld.Greeter server."""

from concurrent import futures
import logging
import threading

import grpc
import chat_pb2
import chat_pb2_grpc
from user import User


class ChatService(chat_pb2_grpc.ChatServiceServicer):

    PORT = 5050
    SERVER_HOST = '10.250.35.25' # gets host IPv4 address
    HEADER = 64
    ADDR = (SERVER_HOST, PORT)
    FORMAT = "utf-8"
    DISCONNECT_MESSAGE = "!DISCONNECT"
    SEPARATE_CHARACTER = "\n"
    VERSION = "1"

    USER_LOCK = threading.Lock()

    USERS = {} # dictionary holding all user objects { key: username, value: user object}

    def LoginClient(self, request, context):
        return self.login_processing(request)

    def CreateAccountClient(self, request, context):
        return self.create_account_processing(request)

    def DeleteAccountClient(self, request, context):
        return self.delete_account_processing(request)

    def ListAccountClient(self, request, context):
        return self.list_account_processing(request)

    def SendMessageClient(self, request, context):
        return self.send_msg_processing(request)

    def ViewMessageClient(self, request, context):
        return self.view_msg_processing(request)

    def LogoutClient(self, request, context):
        return self.logout_processing(request)

    def CheckIncomingMessagesClient(self, request, context):
        return self.check_msg_processing(request)

    def login_processing(self, request):
        with self.USER_LOCK:
            if request.info in self.USERS:
                if not self.USERS[request.info].logged_in:
                    self.USERS[request.info].logged_in = True
                return chat_pb2.ServerMessage(operation=chat_pb2.SUCCESS, info="")
        return chat_pb2.ServerMessage(operation=chat_pb2.ACCOUNT_DOES_NOT_EXIST, info="")

    def create_account_processing(self, request):
        with self.USER_LOCK:
            if request.info in self.USERS:
                return chat_pb2.ServerMessage(operation=chat_pb2.ACCOUNT_ALREADY_EXISTS, info="")
            new_user = User(request.info)
            self.USERS[request.info] = new_user
        return chat_pb2.ServerMessage(operation=chat_pb2.SUCCESS, info="")

    def delete_account_processing(self, request):
        with self.USER_LOCK:
            if request.info in self.USERS and self.USERS[request.info].logged_in:
                del self.USERS[request.info]
                return chat_pb2.ServerMessage(operation=chat_pb2.SUCCESS, info="")
        return chat_pb2.ServerMessage(operation=chat_pb2.ACCOUNT_DOES_NOT_EXIST, info="")

    def list_account_processing(self, request):
        with self.USER_LOCK:
            if not self.USERS:
                return chat_pb2.ServerMessage(operation=chat_pb2.FAILURE, info="")
            else:
                accounts = self.USERS.keys()
                accounts_string = "\n".join(accounts)
                return chat_pb2.ServerMessage(operation=chat_pb2.SUCCESS, info=accounts_string)

    def send_msg_processing(self, request):
        sender, receiver, msg = request.info.split("\n")
        with self.USER_LOCK:
            if receiver in self.USERS and sender in self.USERS:
                self.USERS[receiver].queue_message(msg, deliver_now=self.USERS[receiver].logged_in)
                return chat_pb2.ServerMessage(operation=chat_pb2.SUCCESS, info="")
            else:
                return chat_pb2.ServerMessage(operation=chat_pb2.FAILURE, info="")

    def view_msg_processing(self, request):
        with self.USER_LOCK:
            if request.info in self.USERS:
                if self.USERS[request.info].undelivered_messages.empty(): # handle case of no undelivered messages
                    return chat_pb2.ServerMessage(operation=chat_pb2.NO_MESSAGES, info="")
                messages = self.SEPARATE_CHARACTER.join(self.USERS[request.info].get_current_messages())
                return chat_pb2.ServerMessage(operation=chat_pb2.MESSAGES_EXIST, info=messages)
            return chat_pb2.ServerMessage(operation=chat_pb2.FAILURE, info="")

    def logout_processing(self, request):
        with self.USER_LOCK:
            if request.info in self.USERS and self.USERS[request.info].logged_in:
                self.USERS[request.info].logged_in = False
                return chat_pb2.ServerMessage(operation=chat_pb2.SUCCESS, info="")
        return chat_pb2.ServerMessage(operation=chat_pb2.FAILURE, info="")

    def check_msg_processing(self, request):
        if request.info in self.USERS:
            if self.USERS[request.info].immediate_messages.empty():
                return chat_pb2.ServerMessage(operation=chat_pb2.NO_MESSAGES, info="")
            else:
                messages = self.USERS[request.info].get_current_messages(deliver_now=True)
                message_string = self.SEPARATE_CHARACTER.join(messages)
                return chat_pb2.ServerMessage(operation=chat_pb2.MESSAGES_EXIST, info=message_string)
        print("Failure finding user info")
        return chat_pb2.ServerMessage(operation=chat_pb2.FAILURE, info="")
        
