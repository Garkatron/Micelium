from src.server.server_cmd import Server
from src.client.client_cmd import Client
import argparse


def init():
    a=argparse.ArgumentParser()
    a.add_argument('-c', '--client', action='store_true', help='Config net selector')
    a.add_argument('-s', '--server', action='store_true', help='Config net selector')
    return a.parse_args()
if __name__ == "__main__":
    args=init()
    if args.server:
        s=Server()
    elif args.client:
        c=Client()
