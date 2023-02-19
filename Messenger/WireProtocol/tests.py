from unittest import TestCase
from unittest.mock import MagicMock, patch
from operations import Operations
from client import WireClient


class ClientTests(TestCase):

    def test_login_works(self):
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.SUCCESS, "info": ""}):
            this_client = WireClient()
            self.assertEqual(this_client.login("jothi"), 0)

    def test_login_fails(self):
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.ACCOUNT_DOES_NOT_EXIST, "info": ""}):
            this_client = WireClient()
            self.assertEqual(this_client.login("jothi"), 1)

    def test_create_account_works(self):
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.SUCCESS, "info": ""}):
            this_client = WireClient()
            self.assertEqual(this_client.create_account("jothi"), 0)

    def test_create_account_fails(self):
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.ACCOUNT_ALREADY_EXISTS, "info": ""}):
            this_client = WireClient()  
            self.assertEqual(this_client.create_account("jothi"), 1)

    def test_logout_works(self):
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.SUCCESS, "info": ""}):
            this_client = WireClient() 
            self.assertEqual(this_client.logout("jothi"), 0)

    def test_logout_fails(self):
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.ACCOUNT_DOES_NOT_EXIST, "info": ""}):
            this_client = WireClient() 
            self.assertEqual(this_client.logout("jothi"), 1)

    def test_delete_account_works(self):
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.SUCCESS, "info": ""}):
            this_client = WireClient() 
            self.assertEqual(this_client.delete_account("jothi"), 0)

    def test_delete_account_fails(self):
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.ACCOUNT_DOES_NOT_EXIST, "info": ""}):
            this_client = WireClient() 
            self.assertEqual(this_client.delete_account("jothi"), 1)

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
            self.assertEqual(this_client.view_msgs("jothi"), 0)

    def test_view_msgs_fails(self):
        with patch.object(WireClient, 'send', return_value={"version": 1, "operation": Operations.FAILURE, "info": ""}):
            this_client = WireClient() 
            self.assertEqual(this_client.view_msgs("jothi"), 1)
