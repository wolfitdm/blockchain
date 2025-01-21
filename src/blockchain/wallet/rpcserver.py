import sys
import logging
import signal

from blockchain.wallet.commands.send import SendCommand
from blockchain.wallet.commands.make_address import MakeAddressCommand
from blockchain.wallet.commands.list_addresses import ListAddressesCommand
from blockchain.wallet.commands.sync_ex import SyncCommandEx

def sendMoney(from_address_or_key, amount_txt, to_address_or_key):
    s = SendCommand(from_address_or_key, amount_txt, to_address_or_key)
    return s.get_last_results()

def newAddress(key_name):
    m = MakeAddressCommand(key_name)
    return m.get_last_results() 
    
def listAddresses():
    l = ListAddressesCommand()
    return l.get_last_results()

def syncNetwork():
    s = SyncCommandEx()
    return s.get_last_results()

from blockchain.common.rpc import RPCServer

class BlockchainRPCServer:
    def __init__(self, main_thread=True):
        self.main_thread = main_thread
        self.server = RPCServer()
        self.server.registerMethod(sendMoney)
        self.server.registerMethod(newAddress)
        self.server.registerMethod(listAddresses)
        self.server.registerMethod(syncNetwork)
    def _quit(self, signal, frame):
        logging.info("Stopping BlockchainRPCServer...")
        print("Stopping BlockchainRPCServer...")
        
    def signal_quit(self):
        signal.signal(signal.SIGINT, self._quit)

    def start(self):
        try:
            if self.main_thread:
               self.signal_quit()
            logging.info("Starting BlockchainRPCServer...")
            print("Starting BlockchainRPCServer...")
            self.server.run()
            print("Started BlockchainRPCServer...")
        except KeyboardInterrupt:
            raise KeyboardInterrupt()
