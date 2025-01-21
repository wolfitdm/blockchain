from blockchain.miner.main import MiningServer
from blockchain.wallet.rpcserver import BlockchainRPCServer

import threading
import signal

from multiprocessing import Process
    
def rpcserver_start():
    BlockchainRPCServer().start()

if __name__ == '__main__':
    try:
        miner_server = MiningServer(main_thread=False)
        miner_server.signal_quit()
        blockchain_server = BlockchainRPCServer(main_thread=False)
        blockchain_server.signal_quit()
        miner = threading.Thread(name='miner',target=miner_server.start, daemon=True)
        rpcserver = threading.Thread(name='rpcserver',target=blockchain_server.start, daemon=True)
        miner.start()
        rpcserver.start()
        miner.join()
        rpcserver.join()
    except KeyboardInterrupt:
        signal.raise_signal(signal.SIGINT)