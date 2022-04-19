from hashlib import sha256
import os

from numpy import block
import config
import blockchain
from blockchain.util import encode_as_str
import transaction, persistent

class Blockchain(persistent.Persistent):

    def __init__(self):
        """ Create a new Blockchain object; we store 1 globally in the database.

        Attributes:
            chain (:obj:`dict` of (int to (:obj:`list` of str))): Maps integer chain heights to list of block hashes at that height in the DB (as strings).
            blocks (:obj:`dict` of (str to (:obj:`Block`))): Maps block hashes to their corresponding Block objects in the DB.
            blocks_spending_input (:obj:`dict` of (str to (:obj:`list` of str))): Maps input references as strings to all blocks in the DB that spent them as list of their hashes.
            blocks_containing_tx (:obj:`dict` of (str to (:obj:`list` of str))): Maps transaction hashes to all blocks in the DB that spent them as list of their hashes.
            all_transactions (:obj:`dict` of (str to :obj:`Transaction`)): Maps transaction hashes to their corresponding Transaction objects.
        """
        self.chain = {}
        self.blocks = {}
        self.blocks_spending_input = {}
        self.blocks_containing_tx = {}
        self.all_transactions = {}

    def add_block(self, block, save=True):
        """ Adds a block to the blockchain; the block must be valid according to all block rules.

        Args:
            block (:obj:`Block`): Block to save to the blockchain
            save (bool, optional): Whether to commit changes to database (defaults to True)

        Returns:
            bool: True on success, False otherwise.
        """
        if block.hash in self.blocks:
            return False
        if not block.is_valid()[0]:
            return False
        if not block.height in self.chain:
            self.chain[block.height] = []
        if not block.hash in self.chain[block.height]:
            # add newer blocks to front so they show up first in UI
            self.chain[block.height] = [block.hash] + self.chain[block.height]
        if not block.hash in self.blocks:
            self.blocks[block.hash] = block
        for tx in block.transactions:
            self.all_transactions[tx.hash] = tx
            if not tx.hash in self.blocks_containing_tx:
                self.blocks_containing_tx[tx.hash] = []
            self.blocks_containing_tx[tx.hash].append(block.hash)
            for input_ref in tx.input_refs:
                if not input_ref in self.blocks_spending_input:
                    self.blocks_spending_input[input_ref] = []
                self.blocks_spending_input[input_ref].append(block.hash)
        self._p_changed = True # Marked object as changed so changes get saved to ZODB.
        if save:
            transaction.commit() # If we're going to save the block, commit the transaction.
        return True

    def get_heights_with_blocks(self):
        """ Return all heights in the blockchain that contain blocks.

        Returns:
            (:obj:`list` of int): List of heights in the blockchain with blocks at that location.
        """
        all_heights = list(self.chain.keys())
        all_heights.sort()
        return all_heights

    def get_blockhashes_at_height(self, height):
        """ Return list of hashes of blocks at a particular height stored in the chain database.

        Args:
            height (int): Desired height to query.

        Returns:
            (:obj:`list` of str): list of blockhashes at given height
        """
        return self.chain[height]

    def get_chain_ending_with(self, block_hash):
        """ Return a list of blockhashes in the chain ending with the provided hash, following parent pointers until genesis

        Args:
            block_hash (str): Block hash of highest block in desired chain.

        Returns:
            (:obj:`list` of str): list of all blocks in the chain between desired block and genesis, in the descending order of height. 
        """

        # (hint): you may find the is_genesis flag helpful in this method
        # as well as the self.blocks data structure
        if block_hash in self.blocks.keys():
            hashes = [block_hash]
            currentBlock = self.blocks[block_hash]
            while currentBlock.is_genesis == False:
                parent_hash = currentBlock.parent_hash
                hashes.append(parent_hash)
                currentBlock = self.blocks[parent_hash]
            return hashes
        else:
            return []

    def get_all_block_weights(self):
        """ Get total weight for every block in the blockchain database.
        (eg if a block is at height 3, and all blocks have weight 1, the block will have weight 4 across blocks 0,1,2,3)

        Returns:
            (obj:`dict` of (str to int)): List mapping every blockhash to its total accumulated weight in the blockchain
        """
        block_hashes_to_total_weights = {}
        for height in self.get_heights_with_blocks():
            for block_hash in self.get_blockhashes_at_height(height):
                # dynamic programming; store map of blocks to weights and populate in increasing height order
                block = self.blocks[block_hash]
                block_hashes_to_total_weights[block_hash] = block.get_weight()
                if not block.is_genesis:
                    block_hashes_to_total_weights[block_hash] += block_hashes_to_total_weights[block.parent_hash]
        return block_hashes_to_total_weights

    def get_heaviest_chain_tip(self):
        """ Find the chain tip with the most accumulated total work.
        Note that if blocks are allowed to have different weights, this
        **may not be the block with the highest height**; we are not allowed
        to assume anything about the weight function other than that it will
        return an int.

        Returns:
            (:obj:`Block`): block with the maximum total weight in db.
        """

        block_hashes_to_total_weights = self.get_all_block_weights()
        heaviest_block = None
        for block_hash in block_hashes_to_total_weights:
            block = self.blocks[block_hash]
            weight_in_block = block_hashes_to_total_weights[block_hash]
            if heaviest_block == None or weight_in_block > heaviest_weight:
                heaviest_block = block
                heaviest_weight = weight_in_block

        return heaviest_block

