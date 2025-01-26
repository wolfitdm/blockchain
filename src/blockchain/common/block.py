from blockchain.common.config import config
from blockchain.common.hash import hash_string,hash_string_to_hex
import blockchain.common.encoders
import math

class Block:
    def __init__(self):
        self.transactions = []
        self.nonce = None
        self.previous_block_id = None
        self.id = None

    def add(self, transaction):
        self.transactions.append(transaction)

    def has_transaction(self, transaction):
        return next((True for t in self.transactions if t.id == transaction.id), False)

    def set_nonce(self, nonce):
        self.nonce = nonce

    def is_mineable(self):
        if self.previous_block_id == config.get('genesis_block_id'):
            return True
        return len(self.transactions) >= config.get('block_size') - 1 # mining reward transaction will be added

    def is_mined(self):
        block_hash_bytes = hash_string(blockchain.common.encoders.block_encode(self, False))
        leading_zero_bits = self._count_leading_zero_bits_in_bytes(block_hash_bytes)
        return leading_zero_bits >= config.get('difficulty')

    def _count_leading_zero_bits_in_bytes(self, bytes):
        count = 0

        for b in bytes:
            leading_zero_bits_in_byte = self._count_leading_zero_bits_in_byte(b)
            count += leading_zero_bits_in_byte
            if leading_zero_bits_in_byte < 8:
                return count

        return count

    def _count_leading_zero_bits_in_byte(self, b):
        return 8 - math.floor(math.log(b, 2)) - 1 if b else 8

    def buildMerkleTree(self):
        if len(self.transactions) <= 0:
           return
        """Generates a Merkle Tree and returns the root hash"""
        leaves = []
        layer = []
        for transaction in self.transactions:
            transaction_hash = str(transaction.id)
            leaves.append(transaction_hash)
            layer.append(transaction_hash)
        # Hash the leaves to create the first level of the tree
        layers = []
        # Build the tree upwards
        new_layer = []
        while len(layer) > 1:
            # Pair up the nodes and hash them together
            if len(layer) % 2 != 0:  # If there's an odd number, duplicate the last element
               layer.append(str(layer[-1]))
        
            # Hash each pair of nodes
            new_layer = []
            for i in range(0, len(layer), 2):
                hash_node = str(hash_string_to_hex(str(layer[i]) + str(layer[i + 1])))
                print(hash_node)
                new_layer.append(hash_node)
            layers.append(new_layer)
            layer = new_layer

        layers.append(layer)
        layers.reverse()
        self.merkleRootHash = layer[0]
        self.merkleTree = layers