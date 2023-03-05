from unittest import TestCase
from unittest.mock import patch
from user import User
from server import WireServer
from operations import Operations
from client import WireClient


class ClientTests(TestCase):
    """Tests for the client side operations for this chat service"""

    username = "jothi"
    this_client= WireClient()

    def test_login_works(self):
        """Test that login works in cases when it should."""
        # patching send method to mock the server response
        # this should return 0 on success, 1 on fail
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.SUCCESS, "info": ""}):
            self.assertEqual(self.this_client.login(self.username), 0)

    def test_login_fails(self):
        """Test that login fails in cases when it should."""
        # patching send method to mock the server response
        # this should return 0 on success, 1 on fail
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.ACCOUNT_DOES_NOT_EXIST, "info": ""}):
            self.assertEqual(self.this_client.login(self.username), 1)

    def test_create_account_works(self):
        """Test that create account works in cases when it should."""
        # patching send method to mock the server response
        # this should return 0 on success, 1 on fail
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.SUCCESS, "info": ""}):
            self.assertEqual(self.this_client.create_account(self.username), 0)

    def test_create_account_fails(self):
        """Test that create account fails in cases when it should."""
        # patching send method to mock the server response
        # this should return 0 on success, 1 on fail
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.ACCOUNT_ALREADY_EXISTS, "info": ""}):
            self.assertEqual(self.this_client.create_account(self.username), 1)

    def test_logout_works(self):
        """Test that logout works in cases when it should."""
        # patching send method to mock the server response
        # this should return 0 on success, 1 on fail
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.SUCCESS, "info": ""}):
            self.assertEqual(self.this_client.logout(self.username), 0)

    def test_logout_fails(self):
        """Test that logout fails in cases when it should."""
        # patching send method to mock the server response
        # this should return 0 on success, 1 on fail
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.ACCOUNT_DOES_NOT_EXIST, "info": ""}):
            self.assertEqual(self.this_client.logout(self.username), 1)

    def test_delete_account_works(self):
        """Test that delete account works in cases when it should."""
        # patching send method to mock the server response
        # this should return 0 on success, 1 on fail
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.SUCCESS, "info": ""}):
            self.assertEqual(self.this_client.delete_account(self.username), 0)

    def test_delete_account_fails(self):
        """Test that delete account fails in cases when it should."""
        # patching send method to mock the server response
        # this should return 0 on success, 1 on fail
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.ACCOUNT_DOES_NOT_EXIST, "info": ""}):
            self.assertEqual(self.this_client.delete_account(self.username), 1)

    def test_list_account_works(self):
        """Test that list account works in cases when it should."""
        # patching send method to mock the server response
        # this should return a message string on success, 1 on fail
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.SUCCESS, "info": ""}):
            self.assertNotEqual(self.this_client.list_accounts(), 1)

    def test_list_account_fails(self):
        """Test that list account fails in cases when it should."""
        # patching send method to mock the server response
        # this should return a message string on success, 1 on fail
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.FAILURE, "info": ""}): 
            self.assertEqual(self.this_client.list_accounts(), 1)

    def test_view_msgs_works(self):
        """Test that view message works in cases when it should."""
        # patching send method to mock the server response
        # this should return 0 on success, 1 on fail
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.SUCCESS, "info": ""}): 
            self.assertEqual(self.this_client.view_msgs(self.username), 0)

    def test_view_msgs_fails(self):
        """Test that view message fails in cases when it should."""
        # patching send method to mock the server response
        # this should return 0 on success, 1 on fail
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.FAILURE, "info": ""}):
            self.assertEqual(self.this_client.view_msgs(self.username), 1)

    def test_send_msgs_works(self):
        """Test that send message works in cases when it should."""
        # patching send method to mock the server response
        # this should return 0 on success, 1 on fail
        second_username = "jsod"
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.SUCCESS, "info": ""}):
            self.assertEqual(self.this_client.send_message(self.username, second_username, "hi"), 0)

    def test_send_msgs_fails(self):
        """Test that send message fails in cases when it should."""
        # patching send method to mock the server response
        # this should return 0 on success, 1 on fail
        second_username = "jsod"
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.FAILURE, "info": ""}):
            self.assertEqual(self.this_client.send_message(self.username, second_username, "hi"), 1)

class ServerTests(TestCase):
    """Tests for the server side operations for this chat service"""

    username = "jothi"
    this_server = WireServer()

    def test_create_account_works(self):
        """Test that create account works in cases when it should."""
        self.this_server.USERS = {}
        # testing with null connection because we are not sending anything across the network when testing
        # when the username is not already in USERS, this should succeed
        results = self.this_server.create_account(self.username, None)
        self.assertEqual(results["operation"], Operations.SUCCESS)

    def test_create_account_fails(self):
        """Test that create account fails in cases when it should."""
        self.this_server.USERS = {}
        new_user = User(self.username)
        self.this_server.USERS[self.username] = new_user
        # testing with null connection because we are not sending anything across the network when testing
        # when the username is already in USERS, this should fail
        results = self.this_server.create_account(self.username, None)
        self.assertEqual(results["operation"], Operations.ACCOUNT_ALREADY_EXISTS)

    def test_login_works(self):
        """Test that login works in cases when it should."""
        self.this_server.USERS = {}
        new_user = User(self.username)
        self.this_server.USERS[self.username] = new_user
        # testing with null connection because we are not sending anything across the network when testing
        # when the username is in USERS, this should succeed
        results = self.this_server.login(self.username, None)
        self.assertEqual(results["operation"], Operations.SUCCESS)

    def test_login_fails(self):
        """Test that login fails in cases when it should."""
        self.this_server.USERS = {}
        # testing with null connection because we are not sending anything across the network when testing
        # when the username is not already in USERS, this should fail
        results = self.this_server.login(self.username, None)
        self.assertEqual(results["operation"], Operations.ACCOUNT_DOES_NOT_EXIST)

    def test_logout_works(self):
        """Test that logout works in cases when it should."""
        self.this_server.USERS = {}
        new_user = User(self.username)
        self.this_server.USERS[self.username] = new_user
        # testing with null connection because we are not sending anything across the network when testing
        # when the username is in USERS and logged in, this should succeed, and update logged_in status
        self.this_server.ACTIVE_USERS[self.username] = None
        results = self.this_server.logout(self.username)
        self.assertEqual(results["operation"], Operations.SUCCESS)

    def test_logout_fails(self):
        """Test that logout fails in cases when it should."""
        self.this_server.USERS = {}
        self.this_server.ACTIVE_USERS = {}
        # when the username is not in USERS, this should fail
        results = self.this_server.logout(self.username)
        self.assertEqual(results["operation"], Operations.ACCOUNT_DOES_NOT_EXIST)

        new_user = User(self.username)
        self.this_server.USERS[self.username] = new_user
        # when the user is not logged in, this should fail
        results2 = self.this_server.logout(self.username)
        self.assertEqual(results2["operation"], Operations.ACCOUNT_DOES_NOT_EXIST)

    def test_delete_account_works(self):
        """Test that delete account works in cases when it should."""
        self.this_server.USERS = {}
        new_user = User(self.username)
        self.this_server.USERS[self.username] = new_user

        # testing with null connection because we are not sending anything across the network when testing
        self.this_server.ACTIVE_USERS[self.username] = None
        # when the user exists and is logged in, this should succeed
        results = self.this_server.delete_account(self.username)
        self.assertFalse(self.username in self.this_server.USERS)
        self.assertFalse(self.username in self.this_server.ACTIVE_USERS)
        self.assertEqual(results["operation"], Operations.SUCCESS)

    def test_delete_account_fails(self):
        """Test that delete account fails in cases when it should."""
        self.this_server.USERS = {}
        self.this_server.ACTIVE_USERS = {}
        # when the user doesn't exist, this should fail
        results = self.this_server.delete_account(self.username)
        self.assertEqual(results["operation"], Operations.ACCOUNT_DOES_NOT_EXIST)

        new_user = User(self.username)
        self.this_server.USERS[self.username] = new_user
        # when the user is not logged in, this should fail
        results2 = self.this_server.delete_account(self.username)
        self.assertEqual(results2["operation"], Operations.ACCOUNT_DOES_NOT_EXIST)

    def test_list_account_works(self):
        """Test that list account works in cases when it should."""
        new_user = User(self.username)
        self.this_server.USERS[self.username] = new_user

        # when one user exists, this should succeed and the info string shouldn't be empty
        results = self.this_server.list_accounts()
        self.assertGreater(len(results["info"]), 0)
        self.assertEqual(results["operation"], Operations.SUCCESS)

        second_username = "jsod"
        second_user = User(second_username)
        self.this_server.USERS[second_username] = second_user

        # when multiple users exist, this should succeed and the info string should contain 
        # enter characters
        results2 = self.this_server.list_accounts()
        self.assertGreater(len(results2["info"]), 0)
        self.assertTrue(self.this_server.SEPARATE_CHARACTER in results2["info"])
        self.assertEqual(results2["operation"], Operations.SUCCESS)


    def test_list_account_fails(self):
        """Test that list account fails in cases when it should."""
        self.this_server.USERS = {}
        self.this_server.ACTIVE_USERS = {}
        # when no users exist, this should fail
        results = self.this_server.list_accounts()
        self.assertEqual(results["operation"], Operations.FAILURE)

    def test_view_msgs_works(self):
        """Test that view messages works in cases when it should."""
        self.this_server.USERS = {}
        new_user = User(self.username)
        self.this_server.USERS[self.username] = new_user

        new_user.queue_message("Testing...")

        # if messages exist for a valid user, success should be returned and the queue 
        # should be empty
        results = self.this_server.view_msgs(self.username)
        self.assertGreater(len(results["info"]), 0)
        self.assertEqual(results["operation"], Operations.SUCCESS)
        self.assertTrue(self.this_server.USERS[self.username].undelivered_messages.empty())

        new_user.queue_message("Testing...")
        new_user.queue_message("Testing again...")

        # if messages exist for a valid user, success should be returned and the queue 
        # should be empty, and the messages should be separated by enter characters
        results2 = self.this_server.view_msgs(self.username)
        assert(self.this_server.USERS[self.username].undelivered_messages.empty())
        self.assertGreater(len(results2["info"]), 0)
        self.assertTrue(self.this_server.SEPARATE_CHARACTER in results2["info"])
        self.assertEqual(results2["operation"], Operations.SUCCESS)

    def test_view_msgs_fails(self):
        """Test that view messages fails in cases when it should."""
        self.this_server.USERS = {}
        new_user = User(self.username)
        self.this_server.USERS[self.username] = new_user

        # if the user is invalid, this should fail
        results = self.this_server.view_msgs(self.username)
        self.assertEqual(results["operation"], Operations.FAILURE)

    def test_send_msgs_works(self):
        """Test that send messages works in cases when it should."""
        self.this_server.USERS = {}
        new_user = User(self.username)
        self.this_server.USERS[self.username] = new_user

        second_username = "jsod"
        second_user = User(second_username)
        self.this_server.USERS[second_username] = second_user

        # if all users are valid, this should succeed
        results = self.this_server.send_message(self.username, second_username, "should work")
        self.assertEqual(results["operation"], Operations.SUCCESS)

    def test_send_msgs_fails(self):
        """Test that send messages fails in cases when it should."""
        self.this_server.USERS = {}
        second_username = "jsod"

        # if no user is valid, this should fail
        results = self.this_server.send_message(self.username, second_username, "should fail")
        self.assertEqual(results["operation"], Operations.FAILURE)

        new_user = User(self.username)
        self.this_server.USERS[self.username] = new_user

        # if any user is invalid, this should fail
        results2 = self.this_server.send_message(self.username, second_username, "should fail")
        self.assertEqual(results2["operation"], Operations.FAILURE)
