# Messenger

## This folder contains two versions of a client/server messenger system designed in Python 3 for Harvard's CS 262: Distributed Systems. The messenger system contains the following features:

- The Messenger system operates entirely in the terminal. Many clients can concurrently connect to a single server, and clients may connect from different machines.
- Create an account. Users must supply a unique user name.
- List accounts (or a subset of the accounts, using a text wildcard).
- Send a message to a recipient. If the recipient is logged in, deliver immediately; otherwise queue the message and deliver on demand. If the message is sent to someone who isn't a user, return an error message. Users cannot send messages to themselves.
- Deliver undelivered messages to a particular user that is not logged in. When the user logs in, they have the ability to view any undelivered messages.
- Delete an account. Users are warned before deleting their account that they will lose any unviewed messages in their inbox.

The first implementation of this system uses sockets and a wire protocol detailed below. Messages are serialized and deserialized according to the wire protocol. The second implementation is largely the same but instead uses Google's gRPC.

<img width="1311" alt="Screenshot 2023-02-21 at 11 21 48 PM" src="https://user-images.githubusercontent.com/55005116/220521233-453d7fc9-4706-4bf5-a9bf-d4827d048e00.png">
