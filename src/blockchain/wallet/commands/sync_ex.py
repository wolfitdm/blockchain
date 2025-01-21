from blockchain.wallet.network import Network
from blockchain.common.services.blockchain_updater import BlockchainUpdater
from blockchain.common.blockchain_loader import BlockchainLoader
from blockchain.wallet.unconfirmed_payments_loader import UnconfirmedPaymentsLoader
from blockchain.wallet.commands.send import SendCommand
from blockchain.common.config import config
import signal
import logging
from threading import Event, Timer

class SyncCommandEx:
    NAME  = 'sync'
    NAME_RPC = 'syncNetwork'
    USAGE = '{}'.format(NAME)
    USAGE_RPC = '{}'.format(NAME_RPC)

    def __init__(self, *args):
        if len(args) != 0:
            self.last_print_message = 'wrong number of args for {}'.format(SyncCommand.NAME)
            logging.error(self.last_print_message)
            print(self.last_print_message)
        else:
            self.shutdown_event = Event()
            self.broadcast_interval = config.get('transaction_broadcast_interval_seconds')

            on_status_update = BlockchainUpdater(self._on_new_block).handle_status_update
            self.listener = Network().find_host_to_sync(on_status_update, self.shutdown_event)

            #signal.signal(signal.SIGINT, self._quit)

            self.last_print_message = 'Synchronising with the network, press Ctrl-C to quit'
            print(self.last_print_message)
            self._sync_unconfirmed_payments()
            self._send_unconfirmed_payments()

    def _sync_unconfirmed_payments(self):
        def read_unconfirmed_payments(unconfirmed_payments):
            transactions = unconfirmed_payments.get_transactions()

            def read_blockchain_and_sync(blockchain):
                transactions_to_remove = [t for t in transactions if blockchain.has_transaction(t)]
                for transaction in transactions_to_remove:
                    unconfirmed_payments.remove(transaction)

            if len(transactions):
                BlockchainLoader().process(read_blockchain_and_sync)

        UnconfirmedPaymentsLoader().process(read_unconfirmed_payments)

    def _send_unconfirmed_payments(self):
        def send(unconfirmed_payments):
            for transaction in unconfirmed_payments.get_transactions():
                SendCommand.send_transaction(transaction)

        UnconfirmedPaymentsLoader().process(send)
        self.broadcast_timer = Timer(self.broadcast_interval, self._send_unconfirmed_payments)
        self.broadcast_timer.start()

    def _on_new_block(self, new_block):
        for transaction in new_block.transactions:
            UnconfirmedPaymentsLoader().process(lambda u_p : u_p.remove(transaction))

    def _quit(self, signal, frame):
        self.shutdown_event.set()
        self.listener.close()
        self.broadcast_timer.cancel()
        
    def get_last_results(self):
        return self.last_print_message
