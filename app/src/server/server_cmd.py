from collections.abc import Callable, Iterable, Mapping
import socket  
          
import argparse

from threading import Thread
from functools import partial

from typing import IO, Any
import continuous_threading

import sys, time, os
from concurrent.futures import ThreadPoolExecutor
from cmd2 import Cmd, Cmd2ArgumentParser, with_argparser
from rich.table import Table


from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.prompt import Prompt
from rich.style import Style

from src.middle.FileManager import FileManager, NetConfig
from rich.theme import Theme

class Server(Cmd):
    def __init__(self, completekey: str = "tab", stdin: IO[str] | None = None, stdout: IO[str] | None = None) -> None:
        super().__init__(completekey, stdin, stdout)
        
        # server
        self.__clients=[]
        self.__tindex=0
        self.__threads=[]
        
        custom_theme = Theme({
            "imp": "blink bold red",
            "warning": "blink bold yellow",
            "con": "blink bold green",
            "static_info":"bold yellow"
        })
        self.console=Console(theme=custom_theme)
        
        # Paths
        self.paths={
            
            "Main":os.path.expanduser("~\AppData\Local\MiceliumConfig"),
            "Server":os.path.expanduser("~\AppData\Local\MiceliumConfig\server"),
            
            }
        
        # create folder if not exists
        FileManager.config_folders(self.paths)
        
        # TCofonfig file
        self.__config_file=self.paths["Server"]+"/Config.json"
        
        # Configure file if not exists
        if not os.path.exists(self.__config_file):
            FileManager.config(self.__config_file,NetConfig("127.0.0.1",12345,1).to_json())
            self.config=FileManager.charge_j_data(self.__config_file)
        else:
            self.config=FileManager.charge_j_data(self.__config_file)
        
        self.__show_net_config()
        # Server init   
        self.server=self.create_server(
            self.config["NetConfigs"]["Ip"],
            self.config["NetConfigs"]["Port"],
            self.config["NetConfigs"]["MaxClients"])
        
        # config
        # x.y.z.p [] vesion principal, cada q + caracteristicas, numero precentacion, parches
        self.version=["[0.3.0.20a]","[0.2.0.5a]","[0.1.0.0a]"]
        self.mode=["default"]
        
        self.prompt="[Server]-> "
        
        self.l=continuous_threading.ContinuousThread(target=self.__listen_for_connections,group=None,daemon=True)
        self.__threads.append(self.l)


        # to_ejecute
        self.cmdloop()      
#_______________________________________________________________________________#
    def do_start(self,inp): 
        self.l.start()
        
    # ----------------- # close
    def do_close(self,inp):
        self.close_clients()
        
    # ----------------- # Exit
    def do_exit(self,arg):
        return True
    # ----------------- # clear
    def do_clear(self,args):
        self.console.clear()
    def do_cls(self,args):
        self.console.clear()
        
    # ----------------- # CONFIG
    config_parser = Cmd2ArgumentParser()
    config_parser.add_argument('-n', '--net_config', action='store_true', help='Config net selector')
    config_parser.add_argument('-r', '--reload_config', action='store_true', help='Config net selector')

    config_parser.add_argument('-i', '--ip', type=str, help='Ip var, its str')
    config_parser.add_argument('-p', '--port', type=int, help='Port var, its int')
    config_parser.add_argument('-u', '--max_users', type=int, help='Max users can connect var, its int')
     
    @with_argparser(config_parser)
    def do_config(self,args):
        if args.net_config:
            if args.ip is not None and args.port is not None and args.max_users is not None:
                FileManager.config_net(self.__config_file,NetConfig(args.ip, args.port, args.max_users))     
        
        if args.reload_config:
            self.console.print("Reloading config...", style="imp")

            time.sleep(0.2)
            self.config=FileManager.charge_j_data(self.__config_file)
            
            self.console.print("Config reloaded!", style="con")
        
    # ----------------- # show
    show_config_parser = Cmd2ArgumentParser()
    show_config_parser.add_argument('-n', '--net_config', action='store_true', help='Show netconfig')
    show_config_parser.add_argument('-c', '--config', action='store_true', help='Show netconfig')
    show_config_parser.add_argument('-a', '--all_config', action='store_true', help='Show netconfig')
    show_config_parser.add_argument('-p', '--plugins_config', action='store_true', help='Show netconfig')
    show_config_parser.add_argument('-f', '--folder', action='store_true', help='Show netconfig')

    @with_argparser(show_config_parser)
    def do_show(self,args):
        if args.net_config:
            self.__show_net_config()
    
    # ----------------- # others
    def do_sendmessage(self,inp):
        for c in self.__clients:
            c.send(inp.encode())
            
    def do_carlos(self, line: str) -> None:
        self.console.print("CARLOS CHUPAPIJA!", style="static_info")
        #return super().default(line)
    
    def do_version(self,args):
        self.console.print("[Version]: ",style="static_info")
        self.console.print(self.version[0],style="static_info")
#_______________________________________________________________________________#
    
    def create_server(self,ip:str,port:int,max_clients:int):
        server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server.bind((ip, port))
        server.listen(max_clients)  
        return server
    
    def close_clients(self):
        if len(self.__clients)!=0:   
            for client in self.__clients:   
                client.close()
            self.close()
        else:
            self.close()
            
    def close(self):
        try:
            self.server.shutdown(socket.SHUT_WR)
            #self.server.close()
        except socket.error as e:
            print(e)
            
        if len(self.__threads)!=0:   
            for t in self.__threads:   
                if t.is_alive():
                    t.close()
                    print(t.is_alive())
                    
# private
#_______________________________________________________________________________#
    def __listen_for_connections(self):
        
        c, address = self.server.accept()
        self.__tindex+=1
        c.settimeout(250)
        
        new_thread=continuous_threading.ContinuousThread(target=self.__listen_to_client,args=(c,address,self.__tindex),daemon=True)
        new_thread.start()
        
        self.__threads.append(new_thread)
        self.__clients.append(c)
                    
        print("\n"+'Server-> Got connection from', address)         
        c.send('Server-> Thank you for connecting'.encode())
        
    def __listen_to_client(self,c,a,id):
        try:
            data=c.recv(1024)
            if data:
                match data:
                    case "-ExitConnection":
                        self.__clients.remove(c)
                    
                        print(data)
                    case default:
                        print(data.decode())
                
            else:
                print("Error")
        except:
            c.close()
            self.__threads[id].close()
            print("ERROR")
            return False
         
    def __show_net_config(self):
        # ___________________________________________ #
        Ip=str(self.config["NetConfigs"]["Ip"])
        Port=str(self.config["NetConfigs"]["Port"])
        MaxC=str(self.config["NetConfigs"]["MaxClients"])
        # ___________________________________________ #
        table = Table(title="Netconfigs")
        table.add_column("IP")
        table.add_column("PORT")
        table.add_column("MAX USERS")
        table.add_row(Ip,Port,MaxC)
        # ___________________________________________ #
   
        self.console.print(table)
        
    def __show_plugins(self):
        pass
 
    def __show_folders(self):
        pass
        
    def __set_layout(self):
        l=Layout(name="root")
        # ___________________________________________ #
        l.split(
            Layout(name="other",ratio=1),
            Layout(name="prompt_container",size=7)    
        )
        # ___________________________________________ #
        l["other"].split_row(
            Layout(name="prompt",minimum_size=80),
            Layout(name="messages",ratio=2)
        )
        # ___________________________________________ #
        l["prompt_container"].split_row(
            Layout(name="prompt"),
            Layout(name="info",ratio=2,minimum_size=60)
        )
        # ___________________________________________ #
        l["messages"].add_split(
            )
        
        return l
    
    def __message_bar(self,layout,layout_name,message,I,MAX):

        layout[layout_name].add_split(Layout(Panel(message),size=5))
        I+=1
        if I>=MAX:
            layout[layout_name].unsplit()
            I=0
        

                    
                
        



