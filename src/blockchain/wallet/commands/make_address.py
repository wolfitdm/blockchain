from blockchain.common.crypto import Crypto
import logging

KEY_STORE_DIR = '.'

class MakeAddressCommand:
    NAME  = 'new-address'
    NAME_RPC = 'newAdress'
    USAGE = '{} <address name>'.format(NAME)
    USAGE_RPC = '{} <address name>'.format(NAME_RPC)

    def __init__(self, *args):
        if len(args) != 1:
            self.last_print_message = 'wrong number of args for {}'.format(MakeAddressCommand.NAME)
            logging.error(self.last_print_message)
            print(self.last_print_message)
        else:
            key_name = args[0]
            try:
                key = Crypto().generate_key(key_name)
                self.last_print_message = 'Generated key [{}] with address {}. Key saved in {}'.format(key.name, key.address, key.key_file_path)
                logging.info(self.last_print_message)
                print(self.last_print_message)
            except BaseException as e:
                logging.error(e)

    def get_last_results(self):
        return self.last_print_message