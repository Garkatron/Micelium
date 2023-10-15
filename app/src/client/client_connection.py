import socket,sys
sys.path.append("../middle")
from src.middle.FileManager import NetConfig
import continuous_threading
import threading

class connection:
    def __init__(self,ip:str ,port:int=12345):
        self.conn = socket.socket()
        self.conn.connect((ip, port))
        self.listen_thread=continuous_threading.ContinuousThread(target=self.__listen,daemon=True)
        
    
    def __init__(self,nt:NetConfig):
        self.conn = socket.socket()
        self.conn.connect((nt.ip, nt.port))
        self.listen_thread=continuous_threading.ContinuousThread(target=self.__listen,daemon=True)

    # thraeds
    def __listen(self):
        try:
            
            print(self.conn.recv(1024).decode())
            
        except socket.error as e:
            print(e)
            self.conn.close()
            
    def close(self):
        print("closing...")
        try:
            self.listen_thread.join(60.0)
            
        except threading.ThreadError as e:
            print(e)
        
        try:
            self.conn.shutdown(socket.SHUT_WR)
        except socket.error as e:
            print(e)
            
    def sendtext(self,id:int,message:str):
        self.conn.send(message.encode())