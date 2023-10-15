import socket            
import argparse
import subprocess
import threading
from functools import partial
import sys, time, os
from typing import IO, Any

from concurrent.futures import ThreadPoolExecutor
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.prompt import Prompt
from rich.style import Style
from src.middle.FileManager import NetConfig, FileManager, ServerConfig
from rich.theme import Theme
from cmd2 import Cmd, Cmd2ArgumentParser, with_argparser
from rich.table import Table
from .client_connection import connection
#__________________________________________________________________________#
class Client(Cmd):
    def __init__(self, completekey: str = "tab", stdin: IO[str] | None = None, stdout: IO[str] | None = None) -> None:
        super().__init__(completekey, stdin, stdout)
        
        # vars
        self.config=None
        self.server_list=None
        self.console=Console()    
        
            # net vars
        self.conn=None
        
            # path paths
        self.paths={
            "main":os.path.expanduser("~\AppData\Local\MiceliumConfig"),
            "client":os.path.expanduser("~\AppData\Local\MiceliumConfig\client")
        }
       
            # path ref vars
        self.__config_path=(self.paths["client"]+"\client.json")
        self.__server_list_path=(self.paths["client"]+"\list.json")
        
        # config
        FileManager.config_folders(self.paths)
        
            # client config
        self.__config()
        
            # config cmd
        self.prompt=self.config["name"]
        self.completekey='tab'
        
       
        
        
        # exect
        self.cmdloop()
    
    # Commands
    # _________________________________ # 
    def do_exit(self,inp):
        return True
        
    def do_close(self,inp):
        self.close()
    
    def do_start(self,args):
        self.conn=connection(NetConfig("127.0.0.1",12346,0))
    
    def do_close(self,args):
        if self.conn is not None:
            self.conn.close()
    
    # with args
    # _________________________________ # 
    send_parser = Cmd2ArgumentParser()
    send_parser.add_argument('-m', '--message', action='store_true', help='Config net selector')
    send_parser.add_argument('-i', '--image', action='store_true', help='Config net selector')
    send_parser.add_argument('-c', '--content', type=str, help='Config net selector')

    @with_argparser(send_parser)
    def do_send(self,args):
        if args.message:
            if args.content:
                text=((str(self.prompt)+args.content))
                self.conn.sendtext(0,text)
    
    # _________________________________ # 
    config_parser = Cmd2ArgumentParser()
    config_parser.add_argument('-c', '--client_config', action='store_true', help='Config net selector')
    config_parser.add_argument('-s', '--server_config', action='store_true', help='Config net selector')

    config_parser.add_argument('-sl', '--server_list_config', action="store_true", help='Ip var, its str')
    
    config_parser.add_argument('-p', '--port', type=int, help='Port var, its int')
    config_parser.add_argument('-i', '--ip', type=str, help='Max users can connect var, its int')
    config_parser.add_argument('-n', '--name', type=str, help='Max users can connect var, its int')
     
    @with_argparser(config_parser)
    def do_config(self,args):
        if args.client_config:
            if args.name is not None:
                data={"name":args.name}
                FileManager.config_rw(self.config_path,data)
                
        if args.server_config:
            if args.ip is not None and args.port:
                FileManager.config_rw(self.config_path,ServerConfig(args.ip,args.port,"2").to_json())
       
       
        if args.server_list_config:
            pass
    
    # others
    # _________________________________ #
    def do_clear(self,args):
        self.console.clear()
        
    def do_cls(self,args):
        self.console.clear()

    # private
    # _________________________________ #
    def __sv_list_c(self):
        # server list config
        if not os.path.exists(self.server_list_path):
            FileManager.config(self.server_list_path,ServerConfig("127.0.0.1",12345,"Default").to_json())
            self.server_list=FileManager.charge_j_data(self.server_list_path)
            
        else:
            self.server_list=FileManager.charge_j_data(self.server_list_path)
            
    def __client_c(self):
        
        if not os.path.exists(self.config_path):
            FileManager.config(self.config_path,{"name":"default"})
            self.config=FileManager.charge_j_data(self.config_path)
        else:
            self.config=FileManager.charge_j_data(self.config_path)
        
        
    def __config(self):
        self.__client_c()
        self.__sv_list_c()