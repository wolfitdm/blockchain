# Needed imports
import json
import socket
import inspect
import os
import sys
from threading import Thread

from base64 import b64encode

app_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = "C:/Users/ABC/Downloads/ZeroNet-win-dist-win64/ZeroNet-win-dist-win64/core"
app_dir = os.path.join(app_dir, "../core")
#os.chdir(app_dir)  # Change working dir to zeronet.py dir
sys.path.insert(0, os.path.join(app_dir, "src/lib"))  # External liblary directory
sys.path.insert(0, os.path.join(app_dir, "src"))  # Imports relative to src

from lib import pybitcointools as btctools

SIZE=1024

# rpc.py
class RPCServer:
    def __init__(self, host:str='0.0.0.0', port:int=8888, login_password:str='login:password', priv_key:str='L1NgKMFuEZpMzGDAB5x8UEq8eGcYtgsc1uVsvvkJiyFBbxKctKPF') -> None:
        self.host = host
        self.port = port
        self.address = (host, port)
        self._methods = {}
        btc_priv_key = priv_key
        btc_pub_key = btctools.privkey_to_pubkey(btc_priv_key)
        btc_address = btctools.pubkey_to_address(btc_pub_key)
        self.login_password_sign = btctools.ecdsa_sign(login_password, btc_priv_key)
        self.btc_pub_key = btc_pub_key
        self._registerMethodLogin = {}
        self._callMethodLogin = {}
    
    def registerMethodLogin(self, functionName, login_password, returnIfKeyNotExists=False):
        key = functionName
        if key in self._registerMethodLogin:
           if self._registerMethodLogin[key]:
              return self._registerMethodLogin[key]
        elif returnIfKeyNotExists:
           return False
        self._registerMethodLogin[key] = btctools.ecdsa_verify(login_password, self.login_password_sign, self.btc_pub_key)
        return self._registerMethodLogin[key]
        
    def callMethodLogin(self, functionName, login_password, regMethodExecuted=True):
        if not regMethodExecuted:
           return False
        key = functionName
        if key in self._callMethodLogin:
           if self._callMethodLogin[key]:
              return self._callMethodLogin[key]
        self._callMethodLogin[key] = btctools.ecdsa_verify(login_password, self.login_password_sign, self.btc_pub_key)
        return self._callMethodLogin[key]
        
        
    def methodLogin(self, functionName, login_password):
        key = functionName
        regM = self.registerMethodLogin(functionName, login_password, True)
        callM = self.callMethodLogin(functionName, login_password, regM)
        return regM and callM
        
    # Within RPCServer
    def registerMethod(self, function, login_password='login:password') -> None:
        try:
            functionName = function.__name__
            if not self.registerMethodLogin(functionName, login_password):
               return None
            self._methods.update({functionName : function})
        except:
            raise Exception('A non function object has been passed into RPCServer.registerMethod(self, function)')
            
   # Within RPCServer  
    def registerInstance(self, instance=None, login_password='login:password') -> None:
        try:
            # Regestring the instance's methods
            for functionName, function in inspect.getmembers(instance, predicate=inspect.ismethod):
                if not functionName.startswith('__'):
                   if not self.registerMethodLogin(functionName, login_password):
                      continue
                   self._methods.update({functionName: function})
        except:
            raise Exception('A non class object has been passed into RPCServer.registerInstance(self, instance)')
            
   # Withing RPCServer
    def __handle__(self, client:socket.socket, address:tuple) -> None:
        print(f'Managing requests from {address}.')
        while True:
            functionName = None
            login_password = None
            try:
                functionName, args, kwargs, login_password = json.loads(client.recv(SIZE).decode())
                if not login_password:
                   login_password = 'login:password'
            except: 
                print(f'! Client {address} disconnected.')
                break
            # Showing request Type
            print(f'> {address} : {functionName}({args})')
            if not self.methodLogin(functionName, login_password):
               result = {}
               result["message"] = "not authenticated"
               client.sendall(json.dumps(result).encode())
            else:
                try:
                    response = self._methods[functionName](*args, **kwargs)
                except Exception as e:
                    # Send back exeption if function called by client is not registred 
                    client.sendall(json.dumps(str(e)).encode())
                else:
                    client.sendall(json.dumps(response).encode())

        print(f'Completed requests from {address}.')
        client.close()
        
    # within RPCServer
    def run(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(self.address)
            sock.listen()

            print(f'+ Server {self.address} running')
            while True:
                try:
                    client, address = sock.accept()

                    Thread(target=self.__handle__, args=[client, address]).start()

                except KeyboardInterrupt:
                    print(f'- Server {self.address} interrupted')
                    break
                    
# in rpc.py
class RPCClient:
    def __init__(self, host:str='localhost', port:int=8888, login_password:str='login:password') -> None:
        self.__sock = None
        self.__address = (host, port)
        self.__login_password = login_password
        
    # Within RPCClient
    def connect(self):
        try:
            self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__sock.connect(self.__address)
        except EOFError as e:
            print(e)
            raise Exception('Client was not able to connect.')
    
    def disconnect(self):
        try:
            self.__sock.close()
        except:
            pass
            
    # Within RPCClient
    def __getattr__(self, __name: str):
        def excecute(*args, **kwargs):
            self.__sock.sendall(json.dumps((__name, args, kwargs, self.__login_password)).encode())

            response = json.loads(self.__sock.recv(SIZE).decode())
   
            return response
        
        return excecute