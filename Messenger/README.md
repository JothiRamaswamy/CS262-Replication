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
You should now be in the grpcprotocol directory in each terminal. Now, install gRPC with the following commands
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
