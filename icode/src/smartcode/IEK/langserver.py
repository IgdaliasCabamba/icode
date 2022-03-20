from dataclasses import dataclass
import threading
import waitress
import socket
from twisted.web import server, resource
from twisted.internet import reactor, endpoints

@dataclass
class ServerData:
    host: str
    mode:str
    name: str
    port: int
    service:str
    

def can_connect_to(host:str, port:int) -> bool:
    
    socket_con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    location = (host, port)
    result_of_check = socket_con.connect_ex(location)
    
    if result_of_check == 0:
        #print("Can NOT connect to: ", port)
        return False
        
    else:
        #print("Can connect to: ", port)
        return True

class ICenter:
    
    def __init__(self):
        self.__data = {
            "servers":[]
        }
        self.__used_ports = []
        self.reactor_thread = threading.Thread(target=self.__run_reactor, daemon = False)
        self.reactor_thread.start()
    
    def __run_reactor(self):
        reactor.run(installSignalHandlers=False)    
    
    def __register(self, host, mode, name, port, service):
        new = ServerData(host, mode, name, port, service)
        self.__data["servers"].append(new)
        return new
    
    def get_server_by_name(self, name):
        for x in self.__data["servers"]:
            if x.name == name:
                return x
        return None
    
    def get_port(self, host:str, data:dict) -> int:
        port = None

        if "port" in data.keys():
            port = data["port"]
        
        if port in self.__used_ports:
            port = None
            
        if port is None or not can_connect_to(host, port):
            for possible_port in range(9000, 65535):
                if can_connect_to(host, possible_port) and port not in self.__used_ports:
                    port = possible_port
                    self.__used_ports.append(port)
                    #print("Tryning to connect to: ", port)
                    break
        #print("Connecting to: ", port)
        return port
    
    def get_host(self, data:dict) -> str:
        if "host" in data.keys():
            host = data["host"]
        else:
            host = "0.0.0.0"
        return host
    
    def get_name(self, call, data):
        if "name" in data.keys():
            name = data["name"].lower()
        else:
            name = str(call)
        return name
    
    def get_mode(self, data):
        if "mode" in data.keys():
            mode = data["mode"].lower()
        else:
            mode = "tcp6"
        return mode
    
    def get_service(self, data):
        if "service" in data.keys():
            service = data["service"].lower()
        else:
            service = "reactor"
        return service
    
    def serve(self, call, args:dict) -> tuple:
        #print(self.__data["servers"])
        host = self.get_host(args)
        port = self.get_port(host, args)
        name = self.get_name(call, args)
        mode = self.get_mode(args)
        service = self.get_service(args)

        if service == "reactor":
            if mode == "tcp6":
                endpoint_type = endpoints.TCP6ServerEndpoint
            elif mode == "tcp4":
                endpoint_type = endpoints.TCP4ServerEndpoint
            
            site = server.Site(call())
            endpoint = endpoint_type(reactor, port)
            
            self.__register(host, mode, name, port, service)
            endpoint.listen(site)
            
        elif service == "none":
            self.__register(host, mode, name, port, service)
            call(host, port)
        
        elif service == "wsgi":
            self.__register(host, mode, name, port, service)
            waitress.serve(call, host=host, port=port)

    def run_new_server(self, call:object, args:dict={}, daemon:bool=False) -> object:
        thread = threading.Thread(target=self.serve, args=(call, args), daemon = daemon)
        thread.start()
        return thread

icenter = ICenter()