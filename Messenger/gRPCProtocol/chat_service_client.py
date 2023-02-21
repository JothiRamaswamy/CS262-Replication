from __future__ import print_function

import logging

import grpc
import chat_pb2
import chat_pb2_grpc
from client import Client
from start import start


def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    print("Will try to greet world ...")
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = chat_pb2_grpc.ChatServiceStub(channel)
        this_client = Client()
        start(this_client, stub)


if __name__ == '__main__':
    logging.basicConfig()
    run()