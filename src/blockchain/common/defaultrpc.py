from blockchain.common.rpc import RPCClient
from blockchain.common.rpc import RPCServer
from blockchain.common.config import config

def get_new_rpc_client():
    rpc_host = str(config.get('rpc_client_address'))
    rpc_port = int(config.get('rpc_port'))
    rpc_login_password = str(config.get('rpc_login_password'))
    client = RPCClient(rpc_host, rpc_port, rpc_login_password)
    return client
    
def get_new_rpc_server():
    rpc_host = str(config.get('rpc_address'))
    rpc_port = int(config.get('rpc_port'))
    rpc_login_password = str(config.get('rpc_login_password'))
    rpc_priv_key = str(config.get('rpc_priv_key'))
    server = RPCServer(rpc_host, rpc_port, rpc_login_password, rpc_priv_key)
    return server