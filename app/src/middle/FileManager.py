import json, os, time

class ServerConfig:
    def __init__(self, ip:str, port:int, name:str) -> None:
        self.ip=ip
        self.port=port
        self.name=name
    
    
    def to_json(self):
        config={
            "Test1":{
                "name":self.name,
                "ip":self.ip,
                "port":self.port
            }
        }
        return config
    
class NetConfig:
    def __init__(self, ip:str, port:int, client_number:int) -> None:
        self.ip=ip
        self.port=port
        self.client_number=client_number
    
    
    def to_json(self):
        config={
                "NetConfigs":{"Ip": self.ip, "Port": self.port, "MaxClients": self.client_number},
                }
        return config
    
class FileManager:

    def config(path,jsonf):
        with open(path,'w') as outfile:
            json.dump(jsonf, outfile)
    def config_rw(path,jsont):
        jsonf=json.dumps(jsont,)
            
        with open(path,'w') as outfile:
            outfile.write(jsonf)

    def config_net(path:str, nc:NetConfig):
            
        jsonf=json.dumps(nc.to_json(),)
            
        with open(path,'w') as outfile:
            outfile.write(jsonf)
                        
    def config_folders(paths:[]):
        
        for f in paths:
        
            if not os.path.exists(paths[f]):
                
                print("creating: "+paths[f])
                os.makedirs(paths[f])
                
            else:
                print("Exists: "+f)
                
    def charge_j_data(path):
        
        ConfigExists=os.path.exists(path)
        if ConfigExists:
            print("Open config...")
            with open(path) as outfile:
                    
                data = json.loads(outfile.read())                
                return data
        else:
            print("Not charged...")