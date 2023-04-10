import unittest
import threading
from client import Client
from chat_pb2_grpc import ChatServiceStub
import chat_pb2
import grpc
from server import ChatService

class TestChatApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ChatServicer_thread = threading.Thread(target=ChatService)
        cls.ChatServicer_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.ChatServicer_thread.join()

    def setUp(self):
        self.chat_client = Client()
        self.channel = grpc.insecure_channel('localhost:50051')
        self.stub = ChatServiceStub(self.channel)

    def test_login(self):
        username = "test_user"
        login_result = self.chat_client.login(username, [self.stub])
        self.assertEqual(login_result, 1)

    def test_create_account(self):
        username = "test_user"
        create_result = self.chat_client.create_account(username, [self.stub])
        self.assertEqual(create_result, 1)

    def test_delete_account(self):
        username = "test_user"
        delete_result = self.chat_client.delete_account(username, [self.stub])
        self.assertEqual(delete_result, 1)

    def test_logout(self):
        logout_result = self.chat_client.logout()
        self.assertEqual(logout_result, 0)

    def test_list_accounts(self):
        accounts = self.chat_client.list_accounts([self.stub])
        self.assertEqual(accounts, 1)

    def test_send_message(self):
        sender = "test_sender"
        receiver = "test_receiver"
        msg = "Test message"
        send_result = self.chat_client.send_message(sender, receiver, msg, [self.stub])
        self.assertEqual(send_result, 1)

    def test_view_msgs(self):
        receiver = "test_receiver"
        view_result = self.chat_client.view_msgs(receiver, [self.stub])
        self.assertEqual(view_result, 1)

if __name__ == "__main__":
    unittest.main()
