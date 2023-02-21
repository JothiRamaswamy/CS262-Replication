from unittest import TestCase
from unittest.mock import patch
from user import User
from server import WireServer
from operations import Operations
from client import WireClient


class ClientTests(TestCase):

    username = "jothi"

    def test_login_works(self):
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.SUCCESS, "info": ""}):
            this_client = WireClient()
            self.assertEqual(this_client.login(self.username), 0)

    def test_login_fails(self):
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.ACCOUNT_DOES_NOT_EXIST, "info": ""}):
            this_client = WireClient()
            self.assertEqual(this_client.login(self.username), 1)

    def test_create_account_works(self):
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.SUCCESS, "info": ""}):
            this_client = WireClient()
            self.assertEqual(this_client.create_account(self.username), 0)

    def test_create_account_fails(self):
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.ACCOUNT_ALREADY_EXISTS, "info": ""}):
            this_client = WireClient()  
            self.assertEqual(this_client.create_account(self.username), 1)

    def test_logout_works(self):
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.SUCCESS, "info": ""}):
            this_client = WireClient() 
            self.assertEqual(this_client.logout(self.username), 0)

    def test_logout_fails(self):
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.ACCOUNT_DOES_NOT_EXIST, "info": ""}):
            this_client = WireClient() 
            self.assertEqual(this_client.logout(self.username), 1)

    def test_delete_account_works(self):
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.SUCCESS, "info": ""}):
            this_client = WireClient() 
            self.assertEqual(this_client.delete_account(self.username), 0)

    def test_delete_account_fails(self):
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.ACCOUNT_DOES_NOT_EXIST, "info": ""}):
            this_client = WireClient() 
            self.assertEqual(this_client.delete_account(self.username), 1)

    def test_list_account_works(self):
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.SUCCESS, "info": ""}):
            this_client = WireClient() 
            self.assertNotEqual(this_client.list_accounts(), 1)

    def test_list_account_fails(self):
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.FAILURE, "info": ""}):
            this_client = WireClient() 
            self.assertEqual(this_client.list_accounts(), 1)

    def test_view_msgs_works(self):
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.SUCCESS, "info": ""}):
            this_client = WireClient() 
            self.assertEqual(this_client.view_msgs(self.username), 0)

    def test_view_msgs_fails(self):
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.FAILURE, "info": ""}):
            this_client = WireClient() 
            self.assertEqual(this_client.view_msgs(self.username), 1)

    def test_send_msgs_works(self):
        second_username = "jsod"
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.SUCCESS, "info": ""}):
            this_client = WireClient() 
            self.assertEqual(this_client.send_message(self.username, second_username, "hi"), 0)

    def test_send_msgs_fails(self):
        second_username = "jsod"
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.FAILURE, "info": ""}):
            this_client = WireClient() 
            self.assertEqual(this_client.send_message(self.username, second_username, "hi"), 1)

class ServerTests(TestCase):

    username = "jothi"

    def test_create_account_works(self):
        this_server = WireServer()
        this_server.USERS = {}
        # testing with null connection because we are not sending anything across the network when testing
        results = this_server.create_account(self.username, None)
        self.assertEqual(results["operation"], Operations.SUCCESS)

    def test_create_account_fails(self):
        this_server = WireServer()
        this_server.USERS = {}
        new_user = User(self.username)
        this_server.USERS[self.username] = new_user
        # testing with null connection because we are not sending anything across the network when testing
        results = this_server.create_account(self.username, None)
        self.assertEqual(results["operation"], Operations.ACCOUNT_ALREADY_EXISTS)

    def test_login_works(self):
        this_server = WireServer()
        this_server.USERS = {}
        new_user = User(self.username)
        this_server.USERS[self.username] = new_user
        # testing with null connection because we are not sending anything across the network when testing
        results = this_server.login(self.username, None)
        self.assertEqual(results["operation"], Operations.SUCCESS)

    def test_login_fails(self):
        this_server = WireServer()
        this_server.USERS = {}
        # testing with null connection because we are not sending anything across the network when testing
        results = this_server.login(self.username, None)
        self.assertEqual(results["operation"], Operations.ACCOUNT_DOES_NOT_EXIST)

    def test_logout_works(self):
        this_server = WireServer()
        this_server.USERS = {}
        new_user = User(self.username)
        this_server.USERS[self.username] = new_user
        # testing with null connection because we are not sending anything across the network when testing
        this_server.ACTIVE_USERS[self.username] = None
        results = this_server.logout(self.username)
        self.assertEqual(results["operation"], Operations.SUCCESS)

    def test_logout_fails(self):
        this_server = WireServer()
        this_server.USERS = {}
        this_server.ACTIVE_USERS = []
        results = this_server.logout(self.username)
        self.assertEqual(results["operation"], Operations.ACCOUNT_DOES_NOT_EXIST)

        new_user = User(self.username)
        this_server.USERS[self.username] = new_user
        results2 = this_server.logout(self.username)
        self.assertEqual(results2["operation"], Operations.ACCOUNT_DOES_NOT_EXIST)

    def test_delete_account_works(self):
        this_server = WireServer()
        this_server.USERS = {}
        new_user = User(self.username)
        this_server.USERS[self.username] = new_user

        # testing with null connection because we are not sending anything across the network when testing
        this_server.ACTIVE_USERS[self.username] = None
        results = this_server.delete_account(self.username)
        self.assertFalse(self.username in this_server.USERS)
        self.assertFalse(self.username in this_server.ACTIVE_USERS)
        self.assertEqual(results["operation"], Operations.SUCCESS)

    def test_delete_account_fails(self):
        this_server = WireServer()
        this_server.USERS = {}
        this_server.ACTIVE_USERS = []
        results = this_server.delete_account(self.username)
        self.assertEqual(results["operation"], Operations.ACCOUNT_DOES_NOT_EXIST)

        new_user = User(self.username)
        this_server.USERS[self.username] = new_user
        results2 = this_server.delete_account(self.username)
        self.assertEqual(results2["operation"], Operations.ACCOUNT_DOES_NOT_EXIST)

    def test_list_account_works(self):
        this_server = WireServer()
        new_user = User(self.username)
        this_server.USERS[self.username] = new_user

        results = this_server.list_accounts()
        self.assertGreater(len(results["info"]), 0)
        self.assertEqual(results["operation"], Operations.SUCCESS)

        second_username = "jsod"
        second_user = User(second_username)
        this_server.USERS[second_username] = second_user

        results2 = this_server.list_accounts()
        self.assertGreater(len(results2["info"]), 0)
        self.assertTrue(this_server.SEPARATE_CHARACTER in results2["info"])
        self.assertEqual(results2["operation"], Operations.SUCCESS)


    def test_list_account_fails(self):
        this_server = WireServer()

        results = this_server.list_accounts()
        self.assertEqual(results["operation"], Operations.FAILURE)

    def test_view_msgs_works(self):
        this_server = WireServer()
        this_server.USERS = {}
        new_user = User(self.username)
        this_server.USERS[self.username] = new_user

        new_user.queue_message("Testing...")

        results = this_server.view_msgs(self.username)
        self.assertGreater(len(results["info"]), 0)
        self.assertEqual(results["operation"], Operations.SUCCESS)
        self.assertTrue(this_server.USERS[self.username].undelivered_messages.empty())

        results2 = this_server.view_msgs(self.username)
        self.assertEqual(results2["operation"], Operations.FAILURE)
        self.assertTrue(this_server.USERS[self.username].undelivered_messages.empty())

        new_user.queue_message("Testing...")
        new_user.queue_message("Testing again...")

        results3 = this_server.view_msgs(self.username)
        assert(this_server.USERS[self.username].undelivered_messages.empty())
        self.assertGreater(len(results3["info"]), 0)
        self.assertTrue(this_server.SEPARATE_CHARACTER in results3["info"])
        self.assertEqual(results3["operation"], Operations.SUCCESS)

    def test_view_msgs_fails(self):
        this_server = WireServer()
        this_server.USERS = {}
        new_user = User(self.username)
        this_server.USERS[self.username] = new_user

        results = this_server.view_msgs(self.username)
        self.assertEqual(results["operation"], Operations.FAILURE)

    def test_send_msgs_works(self):
        this_server = WireServer()
        this_server.USERS = {}
        new_user = User(self.username)
        this_server.USERS[self.username] = new_user

        second_username = "jsod"
        second_user = User(second_username)
        this_server.USERS[second_username] = second_user

        results = this_server.send_message(self.username, second_username, "should work")
        self.assertEqual(results["operation"], Operations.SUCCESS)

    def test_send_msgs_fails(self):
        this_server = WireServer()
        this_server.USERS = {}
        new_user = User(self.username)
        this_server.USERS[self.username] = new_user

        second_username = "jsod"

        results = this_server.send_message(self.username, second_username, "should fail")
        self.assertEqual(results["operation"], Operations.FAILURE)

