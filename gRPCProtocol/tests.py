from unittest import TestCase

import chat_pb2
from chat_pb2 import ServerMessage
from chat_pb2 import ClientMessage
from server import ChatService
from user import User
from client import Client



class ClientTests(TestCase):
    """Tests for the client side operations for this chat service"""

    username = "jothi"
    this_client = Client()

    def test_login_works(self):
        """Test that login works in cases when it should."""
        server_msg = ServerMessage(operation=chat_pb2.SUCCESS, info="")
        # this should return 0 on success, 1 on fail, and should update SESSION_INFO
        result = self.this_client.login_processing(self.username, server_msg)
        self.assertEqual(result, 0)
        self.assertEqual(self.this_client.SESSION_INFO["username"], self.username)

    def test_login_fails(self):
        """Test that login fails in cases when it should."""
        server_msg = ServerMessage(operation=chat_pb2.ACCOUNT_DOES_NOT_EXIST, info="")
        # this should return 0 on success, 1 on fail
        result = self.this_client.login_processing(self.username, server_msg)
        self.assertEqual(result, 1)

    def test_create_account_works(self):
        """Test that create account works in cases when it should."""
        server_msg = ServerMessage(operation=chat_pb2.SUCCESS, info="")
        # this should return 0 on success, 1 on fail, and should update SESSION_INFO
        result = self.this_client.create_account_processing(self.username, server_msg)
        self.assertEqual(result, 0)
        self.assertEqual(self.this_client.SESSION_INFO["username"], self.username)

    def test_create_account_fails(self):
        """Test that create account fails in cases when it should."""
        server_msg = ServerMessage(operation=chat_pb2.ACCOUNT_ALREADY_EXISTS, info="")
        # this should return 0 on success, 1 on fail
        result = self.this_client.create_account_processing(self.username, server_msg)
        self.assertEqual(result, 1)

    def test_logout_works(self):
        """Test that logout works in cases when it should."""
        server_msg = ServerMessage(operation=chat_pb2.SUCCESS, info="")
        self.this_client.SESSION_INFO["username"] = self.username
        # this should return 0 on success, 1 on fail, and should update SESSION_INFO
        result = self.this_client.logout_processing(self.username, server_msg)
        self.assertEqual(result, 0)
        self.assertEqual(self.this_client.SESSION_INFO["username"], "")

    def test_logout_fails(self):
        """Test that logout fails in cases when it should."""
        server_msg = ServerMessage(operation=chat_pb2.ACCOUNT_DOES_NOT_EXIST, info="")
        # this should return 0 on success, 1 on fail
        result = self.this_client.logout_processing(self.username, server_msg)
        self.assertEqual(result, 1)

    def test_delete_account_works(self):
        """Test that delete account works in cases when it should."""
        server_msg = ServerMessage(operation=chat_pb2.SUCCESS, info="")
        self.this_client.SESSION_INFO["username"] = self.username
        # this should return 0 on success, 1 on fail, and should update SESSION_INFO
        result = self.this_client.delete_account_processing(self.username, server_msg)
        self.assertEqual(result, 0)
        self.assertEqual(self.this_client.SESSION_INFO["username"], "")

    def test_delete_account_fails(self):
        """Test that delete account fails in cases when it should."""
        server_msg = ServerMessage(operation=chat_pb2.ACCOUNT_DOES_NOT_EXIST, info="")
        # this should return 0 on success, 1 on fail
        result = self.this_client.delete_account_processing(self.username, server_msg)
        self.assertEqual(result, 1)

    def test_list_account_works(self):
        """Test that list account works in cases when it should."""
        server_msg = ServerMessage(operation=chat_pb2.SUCCESS, info="")
        # this should return a message string on success, 1 on fail
        result = self.this_client.list_account_processing(server_msg)
        self.assertNotEqual(result, 1)

    def test_list_account_fails(self):
        """Test that list account fails in cases when it should."""
        server_msg = ServerMessage(operation=chat_pb2.FAILURE, info="")
        # this should return a message string on success, 1 on fail
        result = self.this_client.list_account_processing(server_msg)
        self.assertEqual(result, 1)

    def test_view_msgs_works(self):
        """Test that view messages works in cases when it should."""
        server_msg = ServerMessage(operation=chat_pb2.SUCCESS, info="")
        # this should return 0 on success, 1 on fail
        result = self.this_client.view_message_processing(server_msg)
        self.assertEqual(result, 0)


    def test_view_msgs_fails(self):
        """Test that view messages fails in cases when it should."""
        server_msg = ServerMessage(operation=chat_pb2.FAILURE, info="")
        # this should return 0 on success, 1 on fail
        result = self.this_client.view_message_processing(server_msg)
        self.assertEqual(result, 1)

    def test_send_msgs_works(self):
        """Test that send messages works in cases when it should."""
        server_msg = ServerMessage(operation=chat_pb2.SUCCESS, info="")
        # this should return 0 on success, 1 on fail
        result = self.this_client.send_message_processing(server_msg)
        self.assertEqual(result, 0)

    def test_send_msgs_fails(self):
        """Test that send messages fails in cases when it should."""
        server_msg = ServerMessage(operation=chat_pb2.FAILURE, info="")
        # this should return 0 on success, 1 on fail
        result = self.this_client.send_message_processing(server_msg)
        self.assertEqual(result, 1)

class ServerTests(TestCase):
    """Tests for the server side operations for this chat service"""

    username = "jothi"
    chat = ChatService()

    def test_create_account_works(self):
        """Test that create account works in cases when it should."""
        client_msg = ClientMessage(info=self.username)
        self.chat.USERS = {}
        # when the username is not already in USERS, this should succeed
        results = self.chat.create_account_processing(client_msg)
        self.assertEqual(results.operation, chat_pb2.SUCCESS)

    def test_create_account_fails(self):
        """Test that create account fails in cases when it should."""
        client_msg = ClientMessage(info=self.username)
        self.chat.USERS = {}
        new_user = User(self.username)
        self.chat.USERS[self.username] = new_user
        # when the username is already in USERS, this should fail
        results = self.chat.create_account_processing(client_msg)
        self.assertEqual(results.operation, chat_pb2.ACCOUNT_ALREADY_EXISTS)

    def test_login_works(self):
        """Test that login works in cases when it should."""
        client_msg = ClientMessage(info=self.username)
        self.chat.USERS = {}
        new_user = User(self.username)
        self.chat.USERS[self.username] = new_user
        # when the username is in USERS, this should succeed
        results = self.chat.login_processing(client_msg)
        self.assertEqual(results.operation, chat_pb2.SUCCESS)

    def test_login_fails(self):
        """Test that login fails in cases when it should."""
        client_msg = ClientMessage(info=self.username)
        self.chat.USERS = {}
        # when the username is not already in USERS, this should fail
        results = self.chat.login_processing(client_msg)
        self.assertEqual(results.operation, chat_pb2.ACCOUNT_DOES_NOT_EXIST)

    def test_logout_works(self):
        """Test that logout works in cases when it should."""
        client_msg = ClientMessage(info=self.username)
        self.chat.USERS = {}
        new_user = User(self.username)
        self.chat.USERS[self.username] = new_user
        # when the username is in USERS and logged in, this should succeed, and update logged_in status
        results = self.chat.logout_processing(client_msg)
        self.assertEqual(results.operation, chat_pb2.SUCCESS)
        self.assertFalse(new_user.logged_in)

    def test_logout_fails(self):
        """Test that logout fails in cases when it should."""
        client_msg = ClientMessage(info=self.username)
        self.chat.USERS = {}
        # when the username is not in USERS, this should fail
        results = self.chat.logout_processing(client_msg)
        self.assertEqual(results.operation, chat_pb2.FAILURE)

        new_user = User(self.username)
        self.chat.USERS[self.username] = new_user
        new_user.logged_in = False
        # when the user is not logged in, this should fail
        results2 = self.chat.logout_processing(client_msg)
        self.assertEqual(results2.operation, chat_pb2.FAILURE)

    def test_delete_account_works(self):
        """Test that delete account works in cases when it should."""
        client_msg = ClientMessage(info=self.username)
        self.chat.USERS = {}
        new_user = User(self.username)
        self.chat.USERS[self.username] = new_user

        # when the user exists and is logged in, this should succeed
        results = self.chat.delete_account_processing(client_msg)
        self.assertFalse(self.username in self.chat.USERS)
        self.assertEqual(results.operation, chat_pb2.SUCCESS)

    def test_delete_account_fails(self):
        """Test that delete account fails in cases when it should."""
        client_msg = ClientMessage(info=self.username)
        self.chat.USERS = {}
        # when the user doesn't exist, this should fail
        results = self.chat.delete_account_processing(client_msg)
        self.assertEqual(results.operation, chat_pb2.ACCOUNT_DOES_NOT_EXIST)

        new_user = User(self.username)
        self.chat.USERS[self.username] = new_user
        new_user.logged_in = False
        # when the user is not logged in, this should fail
        results2 = self.chat.delete_account_processing(client_msg)
        self.assertEqual(results2.operation, chat_pb2.ACCOUNT_DOES_NOT_EXIST)

    def test_list_account_works(self):
        """Test that list account works in cases when it should."""
        self.chat.USERS = {}
        new_user = User(self.username)
        self.chat.USERS[self.username] = new_user

        # when one user exists, this should succeed and the info string shouldn't be empty
        results = self.chat.list_account_processing()
        self.assertGreater(len(results.info), 0)
        self.assertEqual(results.operation, chat_pb2.SUCCESS)

        second_username = "jsod"
        second_user = User(second_username)
        self.chat.USERS[second_username] = second_user

        # when multiple users exist, this should succeed and the info string should contain 
        # enter characters
        results2 = self.chat.list_account_processing()
        self.assertGreater(len(results2.info), 0)
        self.assertTrue(self.chat.SEPARATE_CHARACTER in results2.info)
        self.assertEqual(results2.operation, chat_pb2.SUCCESS)

    def test_list_account_fails(self):
        """Test that list account fails in cases when it should."""
        self.chat.USERS = {}

        # when no users exist, this should fail
        results = self.chat.list_account_processing()
        self.assertEqual(results.operation, chat_pb2.FAILURE)

    def test_view_msgs_works(self):
        """Test that view messages works in cases when it should."""
        client_msg = ClientMessage(info=self.username)
        self.chat.USERS = {}
        new_user = User(self.username)
        self.chat.USERS[self.username] = new_user

        # if no messages exist for a valid user, NO_MESSAGES should be returned
        results = self.chat.view_msg_processing(client_msg)
        self.assertEqual(results.operation, chat_pb2.NO_MESSAGES)

        new_user.queue_message("Testing...")

        # if messages exist for a valid user, MESSAGES_EXIST should be returned and the queue 
        # should be empty
        results2 = self.chat.view_msg_processing(client_msg)
        self.assertGreater(len(results2.info), 0)
        self.assertEqual(results2.operation, chat_pb2.MESSAGES_EXIST)
        self.assertTrue(new_user.undelivered_messages.empty())

        new_user.queue_message("Testing...")
        new_user.queue_message("Testing again...")

        # if multiple messages exist for a valid user, MESSAGES_EXIST should be returned, the queue 
        # should be empty, and the messages should be separated by enter characters
        results3 = self.chat.view_msg_processing(client_msg)
        self.assertGreater(len(results3.info), 0)
        self.assertTrue(self.chat.SEPARATE_CHARACTER in results3.info)
        self.assertEqual(results3.operation, chat_pb2.MESSAGES_EXIST)
        self.assertTrue(new_user.undelivered_messages.empty())

    def test_view_msgs_fails(self):
        """Test that view messages fails in cases when it should."""
        client_msg = ClientMessage(info=self.username)
        self.chat.USERS = {}

        # if the user is invalid, this should fail
        results = self.chat.view_msg_processing(client_msg)
        self.assertEqual(results.operation, chat_pb2.FAILURE)

    def test_send_msgs_works(self):
        """Test that send messages works in cases when it should."""
        self.chat.USERS = {}
        new_user = User(self.username)
        self.chat.USERS[self.username] = new_user

        second_username = "jsod"
        second_user = User(second_username)
        self.chat.USERS[second_username] = second_user

        total_info = self.username + "\n" + second_username + "\n" + "hi"
        client_msg = ClientMessage(info=total_info)

        # if all users are valid and the receiver is logged in, this should succeed and the 
        # immediate_messages queue should not be empty
        results = self.chat.send_msg_processing(client_msg)
        self.assertEqual(results.operation, chat_pb2.SUCCESS)
        self.assertFalse(second_user.immediate_messages.empty())
        self.assertTrue(second_user.undelivered_messages.empty())

        # if all users are valid and the receiver is logged out, this should succeed and the 
        # undelivered_messages queue should not be empty
        second_user.logged_in = False
        results = self.chat.send_msg_processing(client_msg)
        self.assertEqual(results.operation, chat_pb2.SUCCESS)
        self.assertFalse(second_user.undelivered_messages.empty())

    def test_send_msgs_fails(self):
        """Test that send messages fails in cases when it should."""
        self.chat.USERS = {}
        second_username = "jsod"

        total_info = self.username + "\n" + second_username + "\n" + "hi"
        client_msg = ClientMessage(info=total_info)
        # if no user is valid, this should fail
        results = self.chat.send_msg_processing(client_msg)
        self.assertEqual(results.operation, chat_pb2.FAILURE)

        new_user = User(self.username)
        self.chat.USERS[self.username] = new_user
        # if any user is invalid, this should fail
        results = self.chat.send_msg_processing(client_msg)
        self.assertEqual(results.operation, chat_pb2.FAILURE)

    def test_check_msgs_works(self):
        """Test that check immediate messages works in cases when it should."""
        client_msg = ClientMessage(info=self.username)
        self.chat.USERS = {}
        new_user = User(self.username)
        self.chat.USERS[self.username] = new_user

        # if no messages exist for a valid user, this should return NO_MESSAGES
        results = self.chat.check_msg_processing(client_msg)
        self.assertEqual(results.operation, chat_pb2.NO_MESSAGES)

        new_user.queue_message("Testing...", deliver_now=True)

        # if messages exist for a valid user, MESSAGES_EXIST should be returned and the queue 
        # should be empty
        results2 = self.chat.check_msg_processing(client_msg)
        self.assertGreater(len(results2.info), 0)
        self.assertEqual(results2.operation, chat_pb2.MESSAGES_EXIST)
        self.assertTrue(new_user.immediate_messages.empty())

        new_user.queue_message("Testing...", deliver_now=True)
        new_user.queue_message("Testing again...", deliver_now=True)

        # if multiple messages exist for a valid user, MESSAGES_EXIST should be returned, the queue 
        # should be empty, and the messages should be separated by enter characters
        results3 = self.chat.check_msg_processing(client_msg)
        self.assertGreater(len(results3.info), 0)
        self.assertTrue(self.chat.SEPARATE_CHARACTER in results3.info)
        self.assertEqual(results3.operation, chat_pb2.MESSAGES_EXIST)
        self.assertTrue(new_user.immediate_messages.empty())

    def test_check_msgs_fails(self):
        """Test that check immediate messages fails in cases when it should."""
        client_msg = ClientMessage(info=self.username)
        self.chat.USERS = {}

        # if the user is invalid, this should fail
        results = self.chat.check_msg_processing(client_msg)
        self.assertEqual(results.operation, chat_pb2.FAILURE)
