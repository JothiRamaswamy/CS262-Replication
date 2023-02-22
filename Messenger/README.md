# Messenger

This folder contains two versions of a client/server messenger system designed in Python 3 for Harvard's CS 262: Distributed Systems. The messenger system contains the following features:


- The Messenger system operates entirely in the terminal. Many clients can concurrently connect to a single server, and clients may connect from different machines.
- Create an account. Users must supply a unique user name.
- List accounts (or a subset of the accounts, using a text wildcard).
- Send a message to a recipient. If the recipient is logged in, deliver immediately; otherwise queue the message and deliver on demand. If the message is sent to someone who isn't a user, return an error message. Users cannot send messages to themselves.
- Deliver undelivered messages to a particular user that is not logged in. When the user logs in, they have the ability to view any undelivered messages.
- Delete an account. Users are warned before deleting their account that they will lose any unviewed messages in their inbox.


The first implementation of this system uses sockets and a wire protocol detailed below. Messages are serialized and deserialized according to the wire protocol. The second implementation is largely the same but instead uses Google's gRPC.


<img width="1311" alt="Screenshot 2023-02-21 at 11 21 48 PM" src="https://user-images.githubusercontent.com/55005116/220521233-453d7fc9-4706-4bf5-a9bf-d4827d048e00.png">

# Setting up Messenger

Open up two terminals, and change the directory of each to the folder in which you'd like this repo to live. Then enter

```
git clone https://github.com/JSOD11/CS262.git
```

# Wire Protocol Setup

To run the wire protocol version of the messenger system, start from the CS262 directory you have cloned, then enter
```
cd messenger/wireprotocol
```
You should now be in the wireprotocol directory in each terminal. Now, designate one of your terminals to be the server. In this terminal, type the following command:
```
python3 start.py server
```
You should should see that the server has started on your machine. In your other open terminal, enter the following command:
```
python3 start.py client
```
Congratulations! You have now set up Messenger on your machine. It is now possible to open more terminals and create more clients, which will all be able to access the server concurrently.

# gRPC Setup

To run the gRPC version of the messenger system, start from the CS262 directory you have cloned, then enter
```
cd messenger/grpcprotocol
```
You should now be in the grpcprotocol directory in each terminal. Now, install gRPC with the following commands:
```
pip3 install grpcio
```
```
pip3 install grpcio-tools
```
Now, designate one of your terminals to be the server. In this terminal, type the following command:
```
python3 start.py server
```
You should should see that the server has started on your machine. In your other open terminal, enter the following command:
```
python3 start.py client
```
Congratulations! You have now set up Messenger on your machine. It is now possible to open more terminals and create more clients, which will all be able to access the server concurrently.

#Wire Protocol: Codebase Structure and Design

The wire protocol version of Messenger contains the following Python files:

- server.py
- client.py
- start.py
- menu.py
- operations.py
- protocols.py
- tests.py
- user.py

### server.py
The server stores all of the current users of Messenger and processes client requests. The server is abstracted into a class called `WireServer` defined in this file which contains important methods such as `handle_client` which determines the nature of a user request and funnels that request to the correct helper function. Other methods such as `login`, `logout`, and `create_account` handle the server-side actions required to successfully complete this request from the perspective of the end user.

### client.py
The client program is what a user of Messenger is ultimately interacting with. The client is abstracted into a class called `WireClient` defined in this file which contains methods such as `login`, `create_account`, and `delete_account`. These methods, once called on the client-side, interact with their counterparts on the server-side through the use of sockets. This communication is made possible by the wire protocol, which determines how clients and the server are able to accurately interpret incoming messages.

### start.py
The `start.py` file is run from the terminal in order to initiate the client or the server. `start.py` imports `WireClient` and `WireServer` from `client.py` and `server.py` and creates objects from the class blueprints that are used within the Messenger application. `start.py` handles linking the client to the server (or vice versa) using sockets. Some client functions including `start` and `load_menu` are included in `start.py` in order to make the code more succint and callable immediately within `start.py` (as opposed to including them in `WireClient`, they instead take the client object as an argument).

### menu.py
The `menu.py` file defines how the user menu behaves using a library called `curses`.

### operations.py
The `operations.py` file defines the unqiue set of operations that will be used within the wire protocol and each an ID.

### protocols.py
The `protocols.py` file defines the `serialize` and `deserialize` functions used to encode messages into a string of bytes or decode a message into its version, operation, and message, which are returned in the form of a dictionary. The `serialize` function wire protocol is to create a data string including the version, operation, and message, in that order. `serialize` is used before a message is sent and `deserialize` is used on a message that was recently received.

### tests.py
The `tests.py` file includes a series of unit tests that confirm that many of the functions in the above files work correctly.

### user.py
The `user.py` file contains the `User` class, which is used by the client and server to keep track of users in the system.
