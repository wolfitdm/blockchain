from threading import Thread
from socket import *
from blockchain.common.utils import text_to_bytes
from blockchain.common.blockchain_loader import BlockchainLoader
import logging

SERVICE_NAME = 'Status Broadcaster'
BROADCAST_ADDRESS = '255.255.255.255'

class StatusBroadcaster(Thread):
    def __init__(self, broadcast_port, block_server_port, broadcast_interval_seconds, shutdown_event):
        Thread.__init__(self)
        self.broadcast_port = broadcast_port
        self.block_server_port = block_server_port
        self.broadcast_interval_seconds = broadcast_interval_seconds
        self.shutdown_event = shutdown_event

    def run(self):
        logging.info('{} started sending to port {}...'.format(SERVICE_NAME, self.broadcast_port))
        while not self.shutdown_event.is_set():
            self._broadcast_status()
            self.shutdown_event.wait(self.broadcast_interval_seconds)
        logging.info('{} shut down'.format(SERVICE_NAME))

    def _broadcast_status(self):
        blockchain_length = self._get_blockchain_status_value()
        status_message_bytes = text_to_bytes('{}:{}'.format(blockchain_length, self.block_server_port))
        s = socket(AF_INET, SOCK_DGRAM)
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        s.sendto(status_message_bytes, (BROADCAST_ADDRESS, self.broadcast_port))
        s.close()
        logging.debug('{} sent {}.'.format(SERVICE_NAME, blockchain_length))

    def _get_blockchain_status_value(self):
        return BlockchainLoader().process(lambda blockchain : len(blockchain.blocks))
