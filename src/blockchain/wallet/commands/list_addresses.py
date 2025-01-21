from blockchain.common.crypto import Crypto
from blockchain.common.config import config
from blockchain.common.blockchain_loader import BlockchainLoader
from blockchain.wallet.unconfirmed_payments_loader import UnconfirmedPaymentsLoader
import os
import logging

class ListAddressesCommand:
    NAME  = 'list-addresses'
    NAME_RPC = 'listAdresses'
    USAGE = '{}'.format(NAME)
    USAGE_RPC = '{}'.format(NAME_RPC)

    def __init__(self, *args):
        self.last_print_message = []
        if len(args) != 0:
            self.last_print_message = []
            self.last_print_message.append('wrong number of args for {}'.format(ListAddressesCommand.NAME))
            logging.error(self.last_print_message[0])
            print(self.last_print_message[0])
        else:
            BlockchainLoader().process(self._show_balances)

    def _show_balances(self, blockchain):
        crypto = Crypto()
        keys = crypto.get_keys()
        self.last_print_message = []
        self.last_print_message.append("Found {} address{} in directory '{}':".format(len(keys), '' if len(keys) == 1 else 'es', os.path.abspath(crypto.key_store_dir)))
        self.last_print_message.append('{:16} {:12} {:12} {:64}'.format('Key Name', 'Balance', 'Pending', 'Address'))
        self.last_print_message.append('{:-<16} {:-<12} {:-<12} {:-<64}'.format('', '', '', ''))
        print(self.last_print_message[0])

        unconfirmed_payment_totals = self._get_unconfirmed_payment_totals(list(map(lambda key : key.address, keys)))

        print(self.last_print_message[1])
        print(self.last_print_message[2])
        for key in keys:
            unconfirmed_payments = '{:+f}'.format(unconfirmed_payment_totals.get(key.address) or 0.0)
            temp = '{:16} {:>12} {:>12} {}'.format(key.name, blockchain.get_balance_for_address(key.address),
                                                  unconfirmed_payments, key.address)
            print(temp)
            self.last_print_message.append(temp)

    def _get_unconfirmed_payment_totals(self, addresses):
        totals = {}
        for address in addresses:
            totals[address] = 0

        def update_totals(unconfirmed_payments):
            for payment in unconfirmed_payments.payments.values():
                if payment.from_address in addresses:
                    totals[payment.from_address] -= payment.amount
                if payment.to_address in addresses:
                    totals[payment.to_address] += payment.amount

        UnconfirmedPaymentsLoader().process(update_totals)

        return totals
        
    def get_last_results(self):
        last_str = '\n'
        return last_str.join(self.last_print_message)
       
