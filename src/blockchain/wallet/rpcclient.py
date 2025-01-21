import sys
import logging

from blockchain.common.rpc import RPCClient
from blockchain.wallet.commands.send import SendCommand
from blockchain.wallet.commands.make_address import MakeAddressCommand
from blockchain.wallet.commands.list_addresses import ListAddressesCommand
from blockchain.wallet.commands.sync import SyncCommand
from blockchain.common.config import update_config_from_args

COMMANDS_NAMES = ["sendMoney", "newAddress", "listAddresses", "syncNetwork"]
COMMANDS = [SendCommand, MakeAddressCommand, ListAddressesCommand, SyncCommand]
USAGE = ' | '.join(map(lambda c : c.USAGE_RPC, COMMANDS))

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    if len(sys.argv) < 2:
        logging.info('Usage: python {} ({})'.format(sys.argv[0], USAGE))
    else:
        server = RPCClient('127.0.0.1', 8888)
        server.connect()
        args = update_config_from_args(sys.argv)
        user_command_name = args[1]
        user_command = None
        if hasattr(server, user_command_name):
           user_command = getattr(server, user_command_name)
        
           if user_command:
              last_results = user_command(*args[2:])
              if last_results:
                 logging.info(last_results)
           else:
              logging.error('Unknown command: {}'.format(user_command_name))
        else:
            logging.error('Unknown command: {}'.format(user_command_name))

        server.disconnect()