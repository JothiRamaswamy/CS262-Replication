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
from operations import ClientOperation, ServerOperation


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
    ACTIVE_USERS = {} # holds currently logged in users { key: username, value: conn}

    def LoginClient(self, request, context):
        with self.USER_LOCK:
            if request.info in self.USERS:
                self.ACTIVE_USERS[request.info] = request.info
                return chat_pb2.ServerMessage(operation=ServerOperation.Value("SUCCESS"), info="")
        return chat_pb2.ServerMessage(operation=ServerOperation.Value("FAILURE"), info="")

    def CreateAccountClient(self, request, context):
        with self.USER_LOCK:
            if request.info in self.USERS:
                return chat_pb2.ServerMessage(operation=ServerOperation.Value("ACCOUNT_ALREADY_EXISTS"), info="")
            new_user = User(request.info)
            self.USERS[request.info] = new_user
            self.ACTIVE_USERS[request.info] = request.info
        return chat_pb2.ServerMessage(operation=ClientOperation.Value("SUCCESS"), info="")

    def DeleteAccountClient(self, request, context):
        with self.USER_LOCK:
            if request.info in self.USERS and request.info in self.ACTIVE_USERS:
                del self.USERS[request.info]
                del self.ACTIVE_USERS[request.info]
                return chat_pb2.ServerMessage(operation=ClientOperation.SUCCESS, info="")
        return chat_pb2.ServerMessage(operation=ServerOperation.ACCOUNT_DOES_NOT_EXIST, info="")

    def ListAccountClient(self, request, context):
        with self.USER_LOCK:
            if not self.USERS:
                return chat_pb2.ServerMessage(operation=ServerOperation.Value("FAILURE"), info="")
            else:
                accounts = self.USERS.keys()
                accounts_string = "\n".join(accounts)
                return chat_pb2.ServerMessage(operation=ClientOperation.Value("SUCCESS"), info=accounts_string)
    
    def SendMessageClient(self, request, context):
        sender, receiver, msg = request.info.split("\n")
        with self.USER_LOCK:
            if receiver in self.USERS:
                if receiver not in self.ACTIVE_USERS:
                    self.USERS[receiver].queue_message(msg)
                    return chat_pb2.ServerMessage(operation=ClientOperation.Value("SUCCESS"), info="")
            else:
                return chat_pb2.ServerMessage(operation=ServerOperation.Value("FAILURE"), info="")

    def ViewMessageClient(self, request, context):
        with self.USER_LOCK:
            if not self.USERS[request.info].undelivered_messages: # handle case of no undelivered messages
                return chat_pb2.ServerMessage(operation=ServerOperation.Value("FAILURE"), info="")
            messages = self.SEPARATE_CHARACTER.join(self.USERS[request.info].get_current_messages())
        return chat_pb2.ServerMessage(operation=ClientOperation.Value("SUCCESS"), info=messages)

    def LogoutClient(self, request, context):
        with self.USER_LOCK:
            if request.info in self.ACTIVE_USERS:
                del self.ACTIVE_USERS[request.info]
                return chat_pb2.ServerMessage(operation=ClientOperation.Value("SUCCESS"), info="")
        return chat_pb2.ServerMessage(operation=ClientOperation.Value("FAILURE"), info="")

    def QuitClient(self, request, context):
        return chat_pb2.ServerMessage(operation=ClientOperation.Value("QUIT_MESSENGER"), info="")