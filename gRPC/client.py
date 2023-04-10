import curses
import threading
from typing import List
from chat_pb2 import ServerMessage
from menu import menu
from chat_pb2_grpc import ChatServiceStub
import chat_pb2


class Client:
    SESSION_INFO = {"username": ""}
    CLIENT_LOCK = threading.Lock()
    RECEIVE_EVENT = threading.Event()

    def login(self, username, stubs: List[ChatServiceStub]):
        try:
            received_info = stubs[0].LoginClient(chat_pb2.ClientMessage(info=username))
        except:
            try:
                received_info = stubs[1].LoginClient(
                    chat_pb2.ClientMessage(info=username)
                )
            except:
                try:
                    received_info = stubs[2].LoginClient(
                        chat_pb2.ClientMessage(info=username)
                    )
                except:
                    return 1

        return self.login_processing(username, received_info)

    def create_account(self, username, stubs: List[ChatServiceStub]):
        fail_count = 0
        try:
            received_info = stubs[0].CreateAccountClient(
                chat_pb2.ClientMessage(info=username)
            )
            print(received_info)
        except:
            fail_count += 1

        try:
            received_info = stubs[1].CreateAccountClient(
                chat_pb2.ClientMessage(info=username)
            )
        except:
            fail_count += 1
        try:
            received_info = stubs[2].CreateAccountClient(
                chat_pb2.ClientMessage(info=username)
            )
        except:
            fail_count += 1
        if fail_count == 3:
            return 1
        return self.create_account_processing(username, received_info)

    def delete_account(self, username, stubs: List[ChatServiceStub]):
        fail_count = 0
        try:
            received_info = stubs[0].DeleteAccountClient(
                chat_pb2.ClientMessage(info=username)
            )
        except:
            fail_count += 1
        try:
            received_info = stubs[1].DeleteAccountClient(
                chat_pb2.ClientMessage(info=username)
            )
        except:
            fail_count += 1
        try:
            received_info = stubs[2].DeleteAccountClient(
                chat_pb2.ClientMessage(info=username)
            )
        except:
            fail_count += 1
        if fail_count == 3:
            return 1
        return self.delete_account_processing(username, received_info)

    def logout(self):
        self.SESSION_INFO["username"] = ""
        return 0

    def list_accounts(self, stubs: List[ChatServiceStub]):
        try:
            received_info = stubs[0].ListAccountClient(chat_pb2.ClientMessage(info=""))
        except:
            try:
                received_info = stubs[1].ListAccountClient(
                    chat_pb2.ClientMessage(info="")
                )
            except:
                try:
                    received_info = stubs[2].ListAccountClient(
                        chat_pb2.ClientMessage(info="")
                    )
                except:
                    return 1

        return self.list_account_processing(received_info)

    def send_message(self, sender, receiver, msg, stubs: List[ChatServiceStub]):
        total_info = sender + "\n" + receiver + "\n" + msg

        fail_count = 0
        try:
            received_info = stubs[0].SendMessageClient(
                chat_pb2.ClientMessage(info=total_info)
            )
        except:
            fail_count += 1
        try:
            received_info = stubs[1].SendMessageClient(
                chat_pb2.ClientMessage(info=total_info)
            )
        except:
            fail_count += 1
        try:
            received_info = stubs[2].SendMessageClient(
                chat_pb2.ClientMessage(info=total_info)
            )
        except:
            fail_count += 1
        if fail_count == 3:
            return 1
        return self.send_message_processing(received_info)

    def view_msgs(self, username, stubs: List[ChatServiceStub]):
        fail_count = 0
        try:
            received_info = stubs[0].ViewMessageClient(
                chat_pb2.ClientMessage(info=username)
            )
        except:
            fail_count += 1
        try:
            received_info = stubs[1].ViewMessageClient(
                chat_pb2.ClientMessage(info=username)
            )
        except:
            fail_count += 1
        try:
            received_info = stubs[2].ViewMessageClient(
                chat_pb2.ClientMessage(info=username)
            )
        except:
            fail_count += 1
        if fail_count == 3:
            return 1
        return self.view_message_processing(received_info)

    def login_processing(self, username, received_info: ServerMessage):
        status = received_info.operation

        if status == chat_pb2.SUCCESS:
            self.SESSION_INFO["username"] = username
            return 0

        elif status == chat_pb2.ACCOUNT_DOES_NOT_EXIST:
            print(
                "\nThe username you entered does not exist on the server. Please try again or input EXIT to exit.\n"
            )
            return 1

    def create_account_processing(self, username, received_info: ServerMessage):
        status = received_info.operation

        if status == chat_pb2.SUCCESS:
            self.SESSION_INFO["username"] = username
            return 0

        print(
            "\nThe username you entered already exists on the server. Please try again or input EXIT to exit.\n"
        )
        return 1

    def delete_account_processing(self, username, received_info: ServerMessage):
        status = received_info.operation

        if status == chat_pb2.SUCCESS:
            self.SESSION_INFO["username"] = ""
            return 0

        print("Deletion failure")
        return 1

    def logout_processing(self, username, received_info: ServerMessage):
        self.SESSION_INFO["username"] = ""
        return 0

    def list_account_processing(self, received_info: ServerMessage):
        status = received_info.operation

        if status == chat_pb2.SUCCESS:
            return received_info

        print("Account information does not exist")
        return 1

    def send_message_processing(self, received_info: ServerMessage):
        status = received_info.operation

        if status == chat_pb2.SUCCESS:
            return 0

        print("Message send failure, receiving account does not exist")
        return 1

    def view_message_processing(self, received_info: ServerMessage):
        if received_info.operation == chat_pb2.NO_MESSAGES:
            print(
                "\n"
                + self.SESSION_INFO["username"]
                + "'s account does not have any unread messages."
            )
            return 1

        messages = received_info.info.split("\n")
        print("\nList of " + self.SESSION_INFO["username"] + "'s messages:\n")
        for j, message in enumerate(messages):
            print(str(j + 1) + ". " + str(message))

        return 0

    def quit_messenger(self):
        self.RECEIVE_EVENT.clear()
        return

    def get_login_input(self, stubs: List[ChatServiceStub]):
        received_list = self.list_accounts(stubs)
        print(received_list)
        if received_list != 1:
            accounts = received_list.info.split("\n")
            message = "\nChoose an account:\n\n"
            username = curses.wrapper(menu, accounts, message)
            return self.login(username, stubs)
        else:
            print("\nThere are currently no accounts on the server.\n")
            input("Press enter to return to the main menu.\n\n")
            return 1
