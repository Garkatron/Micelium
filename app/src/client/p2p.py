from p2pnetwork.node import Node
from collections.abc import Callable, Iterable, Mapping
import socket  
          
import argparse

from threading import Thread
from functools import partial

from typing import IO, Any
import sys, time, os
from concurrent.futures import ThreadPoolExecutor
from cmd2 import Cmd, Cmd2ArgumentParser, with_argparser
from rich.table import Table
import time


from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.prompt import Prompt
from rich.style import Style

from rich.theme import Theme

class P2Pclient(Cmd):
    def __init__(self, completekey: str = "tab", stdin: IO[str] | None = None, stdout: IO[str] | None = None) -> None:
        super().__init__(completekey, stdin, stdout)

        self.n=None
        self.prompt="[P2PC]-> "
        
        
        custom_theme = Theme({
            "imp": "blink bold red",
            "warning": "blink bold yellow",
            "con": "blink bold green",
            "static_info":"bold yellow"
        })
        
        self.console=Console(theme=custom_theme)
        
        self.cmdloop()
    
    create_P = Cmd2ArgumentParser()
    create_P.add_argument('-i', '--ip', type=str, help='Ip var, its str')
    create_P.add_argument('-p', '--port', type=int, help='Port var, its int')
    create_P.add_argument('-d', '--id', type=int, help='Max users can connect var, its int')
    @with_argparser(create_P)
    def do_create(self,args):
        if args.ip is not None and args.port is not None and args.id is not None:

            self.n=self.__create_node(args.ip,args.port,args.id)
        
    def do_start(self,args):
        if self.n is not None:
            self.n.start()
        else:
            print("ERROR")
        
    connect_parser = Cmd2ArgumentParser()
    connect_parser.add_argument('-i', '--ip', type=str, help='Ip var, its str')
    connect_parser.add_argument('-p', '--port', type=int, help='Port var, its int')
    connect_parser.add_argument('-u', '--max_users', type=int, help='Max users can connect var, its int')
    
    @with_argparser(connect_parser)
    def do_connect(self,args):
        if args.ip is not None and args.port is not None:
            self.n.connect_with_node(args.ip, args.port)
        
    message_parser = Cmd2ArgumentParser()
    message_parser.add_argument('-m', '--message', type=str, help='Ip var, its str')

    @with_argparser(message_parser)
    def do_send(self,args):
        if args.message:
            self.n.send_to_nodes(args.message)
            
    def do_exit(self,arg):
        return True
    def do_clear(self,args):
        self.console.clear()
    def do_cls(self,args):
        self.console.clear()
    
    # ____________________________________________________ #
    
    def __node_callback(self,event, node, connected_node, data):
        try:
            if event != 'node_request_to_stop': # node_request_to_stop does not have any connected_node, while it is the main_node that is stopping!
                print('From main node {}: connected node {}: {}'.format(node.id, connected_node.id, data))

        except Exception as e:
            print(e)
            
    def __create_node(self,ip:str,port:int,id:int):
        n = Node(ip,port,id,self.__node_callback)
        return n
        
    

if __name__ =="__main__":
    p=P2Pclient()

    
    

    