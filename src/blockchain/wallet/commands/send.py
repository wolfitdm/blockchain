from blockchain.common.transaction import Transaction
from blockchain.common.crypto import Crypto
from blockchain.common.encoders import transaction_encode
from blockchain.common.utils import text_to_bytes
from blockchain.common.blockchain_loader import BlockchainLoader
from blockchain.wallet.network import Network
from blockchain.wallet.unconfirmed_payments_loader import UnconfirmedPaymentsLoader
from blockchain.common.services.transaction_helper import build_transaction

import re
import logging

ADDRESS_PATTERN = re.compile('^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$')

class SendCommand:
    NAME  = 'send'
    NAME_RPC = 'sendMoney'
    USAGE = '{} <from address> <amount> <to address>'.format(NAME)
    USAGE_RPC = '{} <from address> <amount> <to address>'.format(NAME_RPC)

    def __init__(self, *args):
        if len(args) != 3:
            self.last_print_message = 'wrong number of args for {}'.format(SendCommand.NAME)
            logging.error(self.last_print_message)
            print(self.last_print_message)

        else:
            from_address_or_key, amount_txt, to_address_or_key = args

            crypto = Crypto()
            key = crypto.get_key(from_address_or_key) or crypto.get_key_by_address(from_address_or_key)

            if not key:
                self.last_print_message = 'invalid from address/key'
                logging.error(self.last_print_message)
                print(self.last_print_message)

            elif not (crypto.get_key(to_address_or_key) or self._is_valid_address_format(to_address_or_key)):
                self.last_print_message = 'invalid to address/key'
                logging.error(self.last_print_message)
                print(self.last_print_message)

            elif not self._is_valid_amount_format(amount_txt):
                self.last_print_message = 'invalid amount'
                logging.error(self.last_print_message)
                print(self.last_print_message)

            else:
                balance = BlockchainLoader().process(lambda b : b.get_balance_for_address(key.address))
                amount = float(amount_txt)

                if balance < amount:
                    self.last_print_message = 'Insufficient funds, current balance for this address is {}'.format(balance)
                    logging.error(self.last_print_message)
                    print(self.last_print_message)

                else:
                    to_address_key = crypto.get_key(to_address_or_key)
                    if to_address_key:
                        to_address = to_address_key.address
                    else:
                        to_address = to_address_or_key

                    transaction = build_transaction(key.address, amount, to_address, key)

                    UnconfirmedPaymentsLoader().process(lambda u_p : u_p.add(transaction))

                    SendCommand.send_transaction(transaction)
                    self.last_print_message = 'Send money ({}) from {} to {}!'.format(balance, key.address, to_address)
                    print(self.last_print_message)

    @staticmethod
    def send_transaction(transaction):
        encoded_transaction_text = transaction_encode(transaction)
        encoded_transaction_bytes = text_to_bytes(encoded_transaction_text)

        Network().send_transaction(encoded_transaction_bytes)

    def _is_valid_address_format(self, address_candidate):
        return ADDRESS_PATTERN.match(address_candidate)

    def _is_valid_amount_format(self, amount_txt):
        try:
            return float(amount_txt) > 0
        except ValueError:
            return False

    def get_last_results(self):
        return self.last_print_message
