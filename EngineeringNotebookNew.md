# Engineering Notebook

## Introduction

The provided code consists of two Python files, client.py and server.py, and the necessary protobuf files. The code implements a simple chat system using gRPC, where the client can log in, create an account, delete an account, list accounts, send messages, and view messages. The server-side is implemented using SQLite to store user information and incoming messages.

## client.py

client.py implements the client-side of the chat system. The Client class provides methods to interact with the server using gRPC, and it also provides methods to process the received messages.

The `login()`, `create_account()`, `delete_account()`, `list_accounts()`, `send_message()`, and `view_msgs()` methods use the stubs parameter to connect to the server using gRPC and make requests to the server. If a request fails, the client tries to connect to the next server in the list. If all servers fail, the method returns a failure status code.

The `login_processing()`, `create_account_processing()`, `delete_account_processing()`, `list_account_processing()`, `send_message_processing()`, and `view_message_processing()` methods process the received message from the server and return the appropriate status code based on the operation performed.

## server.py

server.py implements the server-side of the chat system. The ChatService class provides the implementation of the gRPC server. It implements the methods `LoginClient()`, `CreateAccountClient()`, `DeleteAccountClient()`, `ListAccountClient()`, `SendMessageClient()`, `ViewMessageClient()`, `LogoutClient()`, and `CheckIncomingMessagesClient()` that correspond to the methods on the client side.

The `start_db()` method initializes the connection to the SQLite database.

The `is_valid_user()` method checks if a username exists in the database.

The `login_processing()`, `create_account_processing()`, `delete_account_processing()`, and `list_account_processing()` methods interact with the database to perform the requested operation.

The `send_msg_processing()` method sends a message to a user by updating their incoming messages in the database. The `view_msg_processing()` method retrieves the incoming messages for a user and clears them from the database.

The `logout_processing()` method does nothing as there is no session management in this implementation.

The `check_msg_processing()` method is used by the server to periodically check for incoming messages for a user and return them to the user.

## Conclusion

In conclusion, the provided code implements a simple chat system using gRPC and SQLite. The client can log in, create an account, delete an account, list accounts, send messages, and view messages. The server uses SQLite to store user information and incoming messages.