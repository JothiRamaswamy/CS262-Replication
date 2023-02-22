from unittest import TestCase

import chat_pb2
from chat_pb2 import ServerMessage
from chat_pb2 import ClientMessage
from server import ChatService
from user import User
from client import Client



class ClientTests(TestCase):

    username = "jothi"

    def test_login_works(self):
        server_msg = ServerMessage(operation=chat_pb2.SUCCESS, info="")
        this_client = Client()
        result = this_client.login_processing(self.username, server_msg)
        self.assertEqual(result, 0)
        self.assertEqual(this_client.SESSION_INFO["username"], self.username)

    def test_login_fails(self):
        server_msg = ServerMessage(operation=chat_pb2.ACCOUNT_DOES_NOT_EXIST, info="")
        this_client = Client()
        result = this_client.login_processing(self.username, server_msg)
        self.assertEqual(result, 1)

    def test_create_account_works(self):
        server_msg = ServerMessage(operation=chat_pb2.SUCCESS, info="")
        this_client = Client()
        result = this_client.create_account_processing(self.username, server_msg)
        self.assertEqual(result, 0)
        self.assertEqual(this_client.SESSION_INFO["username"], self.username)

    def test_create_account_fails(self):
        server_msg = ServerMessage(operation=chat_pb2.ACCOUNT_ALREADY_EXISTS, info="")
        this_client = Client()
        result = this_client.create_account_processing(self.username, server_msg)
        self.assertEqual(result, 1)

    def test_logout_works(self):
        server_msg = ServerMessage(operation=chat_pb2.SUCCESS, info="")
        this_client = Client()
        this_client.SESSION_INFO["username"] = self.username
        result = this_client.logout_processing(self.username, server_msg)
        self.assertEqual(result, 0)
        self.assertEqual(this_client.SESSION_INFO["username"], "")

    def test_logout_fails(self):
        server_msg = ServerMessage(operation=chat_pb2.ACCOUNT_DOES_NOT_EXIST, info="")
        this_client = Client()
        result = this_client.logout_processing(self.username, server_msg)
        self.assertEqual(result, 1)

    def test_delete_account_works(self):
        server_msg = ServerMessage(operation=chat_pb2.SUCCESS, info="")
        this_client = Client()
        this_client.SESSION_INFO["username"] = self.username
        result = this_client.delete_account_processing(self.username, server_msg)
        self.assertEqual(result, 0)
        self.assertEqual(this_client.SESSION_INFO["username"], "")

    def test_delete_account_fails(self):
        server_msg = ServerMessage(operation=chat_pb2.ACCOUNT_DOES_NOT_EXIST, info="")
        this_client = Client()
        result = this_client.delete_account_processing(self.username, server_msg)
        self.assertEqual(result, 1)

    def test_list_account_works(self):
        server_msg = ServerMessage(operation=chat_pb2.SUCCESS, info="")
        this_client = Client() 
        result = this_client.list_account_processing(server_msg)
        self.assertNotEqual(result, 1)

    def test_list_account_fails(self):
        server_msg = ServerMessage(operation=chat_pb2.FAILURE, info="")
        this_client = Client() 
        result = this_client.list_account_processing(server_msg)
        self.assertEqual(result, 1)

    def test_view_msgs_works(self):
        server_msg = ServerMessage(operation=chat_pb2.SUCCESS, info="")
        this_client = Client() 
        result = this_client.view_message_processing(server_msg)
        self.assertEqual(result, 0)


    def test_view_msgs_fails(self):
        server_msg = ServerMessage(operation=chat_pb2.FAILURE, info="")
        this_client = Client() 
        result = this_client.view_message_processing(server_msg)
        self.assertEqual(result, 1)


    def test_send_msgs_works(self):
        server_msg = ServerMessage(operation=chat_pb2.SUCCESS, info="")
        this_client = Client() 
        result = this_client.send_message_processing(server_msg)
        self.assertEqual(result, 0)

    def test_send_msgs_fails(self):
        server_msg = ServerMessage(operation=chat_pb2.FAILURE, info="")
        this_client = Client() 
        result = this_client.send_message_processing(server_msg)
        self.assertEqual(result, 1)

class ServerTests(TestCase):

    username = "jothi"

    chat = ChatService()

    def test_create_account_works(self):
        client_msg = ClientMessage(operation=chat_pb2.CREATE_ACCOUNT, info=self.username)
        self.chat.USERS = {}
        results = self.chat.create_account_processing(client_msg)
        self.assertEqual(results.operation, chat_pb2.SUCCESS)

    def test_create_account_fails(self):
        client_msg = ClientMessage(operation=chat_pb2.CREATE_ACCOUNT, info=self.username)
        self.chat.USERS = {}
        new_user = User(self.username)
        self.chat.USERS[self.username] = new_user
        results = self.chat.create_account_processing(client_msg)
        self.assertEqual(results.operation, chat_pb2.ACCOUNT_ALREADY_EXISTS)

    def test_login_works(self):
        client_msg = ClientMessage(operation=chat_pb2.LOGIN, info=self.username)
        self.chat.USERS = {}
        new_user = User(self.username)
        self.chat.USERS[self.username] = new_user
        results = self.chat.login_processing(client_msg)
        self.assertEqual(results.operation, chat_pb2.SUCCESS)

    def test_login_fails(self):
        client_msg = ClientMessage(operation=chat_pb2.LOGIN, info=self.username)
        self.chat.USERS = {}
        results = self.chat.login_processing(client_msg)
        self.assertEqual(results.operation, chat_pb2.ACCOUNT_DOES_NOT_EXIST)

    def test_logout_works(self):
        client_msg = ClientMessage(operation=chat_pb2.LOGOUT, info=self.username)
        self.chat.USERS = {}
        new_user = User(self.username)
        self.chat.USERS[self.username] = new_user
        results = self.chat.logout_processing(client_msg)
        self.assertEqual(results.operation, chat_pb2.SUCCESS)
        self.assertFalse(new_user.logged_in)

    def test_logout_fails(self):
        client_msg = ClientMessage(operation=chat_pb2.LOGOUT, info=self.username)
        self.chat.USERS = {}
        results = self.chat.logout_processing(client_msg)
        self.assertEqual(results.operation, chat_pb2.FAILURE)

        new_user = User(self.username)
        self.chat.USERS[self.username] = new_user
        new_user.logged_in = False
        results2 = self.chat.logout_processing(client_msg)
        self.assertEqual(results2.operation, chat_pb2.FAILURE)

        new_user.logged_in = False
        results3 = self.chat.logout_processing(client_msg)
        self.assertEqual(results3.operation, chat_pb2.FAILURE)

    def test_delete_account_works(self):
        client_msg = ClientMessage(operation=chat_pb2.DELETE_ACCOUNT, info=self.username)
        self.chat.USERS = {}
        new_user = User(self.username)
        self.chat.USERS[self.username] = new_user

        results = self.chat.delete_account_processing(client_msg)
        self.assertFalse(self.username in self.chat.USERS)
        self.assertEqual(results.operation, chat_pb2.SUCCESS)

    def test_delete_account_fails(self):
        client_msg = ClientMessage(operation=chat_pb2.DELETE_ACCOUNT, info=self.username)
        self.chat.USERS = {}
        results = self.chat.delete_account_processing(client_msg)
        self.assertEqual(results.operation, chat_pb2.ACCOUNT_DOES_NOT_EXIST)

        new_user = User(self.username)
        self.chat.USERS[self.username] = new_user
        new_user.logged_in = False
        results2 = self.chat.delete_account_processing(client_msg)
        self.assertEqual(results2.operation, chat_pb2.ACCOUNT_DOES_NOT_EXIST)

    def test_list_account_works(self):
        client_msg = ClientMessage(operation=chat_pb2.LIST_ACCOUNTS, info=self.username)
        self.chat.USERS = {}
        new_user = User(self.username)
        self.chat.USERS[self.username] = new_user

        results = self.chat.list_account_processing(client_msg)
        self.assertGreater(len(results.info), 0)
        self.assertEqual(results.operation, chat_pb2.SUCCESS)

        second_username = "jsod"
        second_user = User(second_username)
        self.chat.USERS[second_username] = second_user

        results2 = self.chat.list_account_processing(client_msg)
        self.assertGreater(len(results2.info), 0)
        self.assertTrue(self.chat.SEPARATE_CHARACTER in results2.info)
        self.assertEqual(results2.operation, chat_pb2.SUCCESS)


    def test_list_account_fails(self):
        client_msg = ClientMessage(operation=chat_pb2.LIST_ACCOUNTS, info=self.username)
        self.chat.USERS = {}

        results = self.chat.list_account_processing(client_msg)
        self.assertEqual(results.operation, chat_pb2.FAILURE)

    def test_view_msgs_works(self):
        client_msg = ClientMessage(operation=chat_pb2.VIEW_UNDELIVERED_MESSAGES, info=self.username)
        self.chat.USERS = {}
        new_user = User(self.username)
        self.chat.USERS[self.username] = new_user

        results = self.chat.view_msg_processing(client_msg)
        self.assertEqual(results.operation, chat_pb2.NO_MESSAGES)

        new_user.queue_message("Testing...")

        results2 = self.chat.view_msg_processing(client_msg)
        self.assertGreater(len(results2.info), 0)
        self.assertEqual(results2.operation, chat_pb2.MESSAGES_EXIST)
        self.assertTrue(new_user.undelivered_messages.empty())

        new_user.queue_message("Testing...")
        new_user.queue_message("Testing again...")

        results3 = self.chat.view_msg_processing(client_msg)
        self.assertGreater(len(results3.info), 0)
        self.assertTrue(self.chat.SEPARATE_CHARACTER in results3.info)
        self.assertEqual(results3.operation, chat_pb2.MESSAGES_EXIST)
        self.assertTrue(new_user.undelivered_messages.empty())

    def test_view_msgs_fails(self):
        client_msg = ClientMessage(operation=chat_pb2.VIEW_UNDELIVERED_MESSAGES, info=self.username)
        self.chat.USERS = {}

        results = self.chat.view_msg_processing(client_msg)
        self.assertEqual(results.operation, chat_pb2.FAILURE)

    def test_send_msgs_works(self):
        self.chat.USERS = {}
        new_user = User(self.username)
        self.chat.USERS[self.username] = new_user

        second_username = "jsod"
        second_user = User(second_username)
        self.chat.USERS[second_username] = second_user

        total_info = self.username + "\n" + second_username + "\n" + "hi"
        client_msg = ClientMessage(operation=chat_pb2.SEND_MESSAGE, info=total_info)

        results = self.chat.send_msg_processing(client_msg)
        self.assertEqual(results.operation, chat_pb2.SUCCESS)
        self.assertFalse(second_user.immediate_messages.empty())
        self.assertTrue(second_user.undelivered_messages.empty())

        second_user.logged_in = False
        results = self.chat.send_msg_processing(client_msg)
        self.assertEqual(results.operation, chat_pb2.SUCCESS)
        self.assertFalse(second_user.undelivered_messages.empty())

    def test_send_msgs_fails(self):
        self.chat.USERS = {}
        new_user = User(self.username)
        self.chat.USERS[self.username] = new_user

        second_username = "jsod"

        total_info = self.username + "\n" + second_username + "\n" + "hi"
        client_msg = ClientMessage(operation=chat_pb2.SEND_MESSAGE, info=total_info)
        results = self.chat.send_msg_processing(client_msg)
        self.assertEqual(results.operation, chat_pb2.FAILURE)

    def test_check_msgs_works(self):
        client_msg = ClientMessage(operation=chat_pb2.RECEIVE_CURRENT_MESSAGE, info=self.username)
        self.chat.USERS = {}
        new_user = User(self.username)
        self.chat.USERS[self.username] = new_user

        results = self.chat.check_msg_processing(client_msg)
        self.assertEqual(results.operation, chat_pb2.NO_MESSAGES)

        new_user.queue_message("Testing...", deliver_now=True)

        results2 = self.chat.check_msg_processing(client_msg)
        self.assertGreater(len(results2.info), 0)
        self.assertEqual(results2.operation, chat_pb2.MESSAGES_EXIST)
        self.assertTrue(new_user.immediate_messages.empty())

        new_user.queue_message("Testing...", deliver_now=True)
        new_user.queue_message("Testing again...", deliver_now=True)

        results3 = self.chat.check_msg_processing(client_msg)
        self.assertGreater(len(results3.info), 0)
        self.assertTrue(self.chat.SEPARATE_CHARACTER in results3.info)
        self.assertEqual(results3.operation, chat_pb2.MESSAGES_EXIST)
        self.assertTrue(new_user.immediate_messages.empty())

    def test_check_msgs_fails(self):
        client_msg = ClientMessage(operation=chat_pb2.RECEIVE_CURRENT_MESSAGE, info=self.username)
        self.chat.USERS = {}

        results = self.chat.check_msg_processing(client_msg)
        self.assertEqual(results.operation, chat_pb2.FAILURE)

