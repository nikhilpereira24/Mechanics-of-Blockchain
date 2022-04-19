from abc import ABC, abstractmethod
from unittest import skip # We want to make Block an abstract class; either a PoW or PoA block
import blockchain
from blockchain.util import sha256_2_string, encode_as_str
import time
import persistent
from blockchain.util import nonempty_intersection
from math import ceil, log2

class Block(ABC, persistent.Persistent):

    def __init__(self, height, transactions, parent_hash, is_genesis=False, include_merkle_root=True):
        """ Creates a block template (unsealed).

        Args:
            height (int): height of the block in the chain (# of blocks between block and genesis).
            transactions (:obj:`list` of :obj:`Transaction`): ordered list of transactions in the block.
            parent_hash (str): the hash of the parent block in the blockchain.
            is_genesis (bool, optional): True only if the block is a genesis block.

        Attributes:
            parent_hash (str): the hash of the parent block in blockchain.
            height (int): height of the block in the chain (# of blocks between block and genesis).
            transactions (:obj:`list` of :obj:`Transaction`): ordered list of transactions in the block.
            timestamp (int): Unix timestamp of the block.
            target (int): Target value for the block's seal to be valid (different for each seal mechanism)
            is_genesis (bool): True only if the block is a genesis block (first block in the chain).
            merkle (str): Merkle hash of the list of transactions in a block, uniquely identifying the list.
            seal_data (int): Seal data for block (in PoW this is the nonce satisfying the PoW puzzle; in PoA, the signature of the authority").
            hash (str): Hex-encoded SHA256^2 hash of the block header (self.header()).
        """
        self.parent_hash = parent_hash
        self.height = height
        self.transactions = transactions
        self.timestamp = int(time.time())
        self.target = self.calculate_appropriate_target()
        self.is_genesis = is_genesis
        
        if include_merkle_root:
            self.merkle = self.calculate_merkle_root()
        else:
            self.merkle = sha256_2_string("".join([str(x) for x in self.transactions]))

        self.seal_data = 0 # temporarily set seal_data to 0
        self.hash = self.calculate_hash() # keep track of hash for caching purposes

    def calculate_merkle_root(self):
        """ Gets the Merkle root hash for a given list of transactions.

        This method is incomplete!  Right now, it only hashes the
        transactions together, which does not enable the same type
        of lite client support a true Merkle hash would.

        Follow the description in the problem sheet to calculte the merkle root. 
        If there is no transaction, return SHA256(SHA256("")).
        If there is only one transaction, the merkle root is the transaction hash.
        For simplicity, when computing H(AB) = SHA256(SHA256(H(A) + H(B))), directly double-hash the hex string of H(A) concatenated with H(B).
        E.g., H(A) = 0x10, H(B) = 0xff, then H(AB) = SHA256(SHA256("10ff")).

        Returns:
            str: Merkle root hash of the list of transactions in a block, uniquely identifying the list.
        """
        if len(self.transactions) == 0:
            return sha256_2_string("")
        elif len(self.transactions) == 1:
            return sha256_2_string(str(self.transactions[0]))
        else:
            total = len(self.transactions)
            levels = 1 + ceil(log2(total))
            treenodes = [None] * levels
            for i in range(levels):
                treenodes[i] = [None] * (1 << i)

            level = levels - 1
            for i in range(1 << level):
                if i < len(self.transactions):
                    treenodes[level][i] = sha256_2_string(str(self.transactions[i]))
                else:
                    treenodes[level][i] = sha256_2_string("")
            while level > 0:
                level = level - 1
                for i in range(1 << level):
                    treenodes[level][i] = sha256_2_string(treenodes[level + 1][2*i] + treenodes[level + 1][2*i + 1])

            return treenodes[0][0]

    def unsealed_header(self):
        """ Computes the header string of a block (the component that is sealed by mining).

        Returns:
            str: String representation of the block header without the seal.
        """
        return encode_as_str([self.height, self.timestamp, self.target, self.parent_hash, self.is_genesis, self.merkle], sep='`')

    def header(self):
        """ Computes the full header string of a block after mining (includes the seal).

        Returns:
            str: String representation of the block header.
        """
        return encode_as_str([self.unsealed_header(), self.seal_data], sep='`')

    def calculate_hash(self):
        """ Get the SHA256^2 hash of the block header.

        Returns:
            str: Hex-encoded SHA256^2 hash of self.header()
        """
        return sha256_2_string(str(self.header()))

    def __repr__(self):
        """ Get a full representation of a block as string, for debugging purposes; includes all transactions.

        Returns:
            str: Full and unique representation of a block and its transactions.
        """
        return encode_as_str([self.header(), "!".join([str(tx) for tx in self.transactions])], sep="`")

    def set_seal_data(self, seal_data):
        """ Adds seal data to a block, recomputing the block's hash for its changed header representation.
        This method should never be called after a block is added to the blockchain!

        Args:
            seal_data (int): The seal data to set.
        """
        self.seal_data = seal_data
        self.hash = self.calculate_hash()

    def is_valid(self):
        """ Check whether block is fully valid according to block rules.

        Includes checking for no double spend, that all transactions are valid, that all header fields are correctly
        computed, etc.

        Returns:
            bool, str: True if block is valid, False otherwise plus an error or success message.
        """

        chain = blockchain.chain # This object of type Blockchain may be useful

        # Placeholder for (1a)

        # (checks that apply to all blocks)
        # Check that Merkle root calculation is consistent with transactions in block (use the calculate_merkle_root function) [test_rejects_invalid_merkle]
        # On failure: return False, "Merkle root failed to match"
        if self.calculate_merkle_root() != self.merkle:
            return False, "Merkle root failed to match"
    
        # Check that block.hash is correctly calculated [test_rejects_invalid_hash]
        # On failure: return False, "Hash failed to match"
        if self.calculate_hash() != self.hash:
            return False, "Hash failed to match"


        # Check that there are at most 900 transactions in the block [test_rejects_too_many_txs]
        # On failure: return False, "Too many transactions"
        if len(self.transactions) > 900:
            return False, "Too many transactions"

        # (checks that apply to genesis block)
            # Check that height is 0 and parent_hash is "genesis" [test_invalid_genesis]
            # On failure: return False, "Invalid genesis"
        if self.is_genesis: #if the block is a genesis block
            #if the height is not 0 or the parent hash is not "genesis"
            if self.height != 0 or self.parent_hash != 'genesis': 
                return False, "Invalid genesis"
        # (checks that apply only to non-genesis blocks)
        else:
        # # Check that parent exists (you may find chain.blocks helpful) [test_nonexistent_parent]
            try:
                chain.blocks[self.parent_hash]
            except KeyError:  
        # # On failure: return False, "Nonexistent parent"
                return False, 'Nonexistent parent'

            # Check that height is correct w.r.t. parent height [test_bad_height]
            if chain.blocks[self.parent_hash].height + 1 != self.height:
            # On failure: return False, "Invalid height"
                return False, "Invalid height"

            # Check that timestamp is non-decreasing [test_bad_timestamp]
            # On failure: return False, "Invalid timestamp"
            if self.timestamp < chain.blocks[self.parent_hash].timestamp:
                return False, "Invalid timestamp"


            # Check that seal is correctly computed and satisfies "target" requirements; use the provided seal_is_valid method [test_bad_seal]
            # On failure: return False, "Invalid seal"
            if self.seal_is_valid() == False:
                return False, "Invalid seal"

            seen_txs = {}
            #get the list of block hashes for this chain referencing the parent hash
            blocks_on_chain = chain.get_chain_ending_with(self.parent_hash)
            for tx in self.transactions:
                # Check that all transactions within are valid (use tx.is_valid) [test_malformed_txs]
                # On failure: return False, "Malformed transaction included"
                if tx.is_valid() == False:
                    return False, "Malformed transaction included"
                # Check that for every transaction
                # the transaction has not already been included on a block on the same blockchain as this block [test_double_tx_inclusion_same_chain]
                # # (you may find chain.get_chain_ending_with and chain.blocks_containing_tx and util.nonempty_intersection useful)
                # the transaction has not already been included on a block on the same blockchain as this block [test_double_tx_inclusion_same_chain]
                if blockchain.util.nonempty_intersection(blocks_on_chain, chain.blocks_containing_tx.get(tx.hash, [])):
                    return False, "Double transaction inclusion"
                # # (or twice in this block; you will have to check this manually) [test_double_tx_inclusion_same_block]
                if tx not in seen_txs.values(): #checks for duplicate transactions in block in my seen transactions
                    seen_txs[tx.hash] = tx #add the seen trasanction to a dictionary of seen transactions for this block
                else:
                    #twice on block
                    return False, "Double transaction inclusion"
                
                # for every input ref in the tx
                user = None
                users_balance_in = 0
                for ref in tx.input_refs:
                    # (you may find the string split method for parsing the input into its components)
                    components = ref.split(':')
                    tx_hash, tx_index = components[0], int(components[1])
                    # each input_ref is valid (aka corresponding transaction can be looked up in its holding transaction) [test_failed_input_lookup]
                    # (you may find chain.all_transactions useful here)
                    if tx_hash in chain.all_transactions: #if the input reference is in the chains all transactions this is valid
                        #holding transaction that supposedly funds this current transaction included in this block
                        holding_tx = chain.all_transactions[tx_hash]
                    elif tx_hash in seen_txs.keys(): #if the transaction hash is in the current block this is valid
                        #holding transaction that supposedly funds this current transaction included this block 
                        holding_tx = seen_txs[tx_hash] 
                    else:
                        # On failure: return False, "Required output not found" - Input reference doesnt exist anywhere
                        return False, "Required output not found"
                    
                    #if the transaction output index of the input reference is out of bounds
                    if tx_index >= len(holding_tx.outputs):
                        return False, "Required output not found"

                    #current transaction references exists and is valid
                    # every input was sent to the same user (would normally carry a signature from this user; we leave this out for simplicity) [test_user_consistency]
                    holding_transaction_outputs = holding_tx.outputs[tx_index]
                    if user and holding_transaction_outputs.receiver != user: #no more than one input user once it has been sent
                        #Only one user allowed on the transaction
                        #print(' User Input Consistency: The input user for the next transaction is ', user, 'but instead is ', holding_transaction_outputs.receiver)
                        #The input for this transaction was supposed to Bob but instead received Alice on another ref which should not be the input user
                        #more than one input user
                        return False, "User inconsistencies"
                    else:
                        #set user for the transaction as the holding (funding) transactions reciever
                        user = holding_transaction_outputs.receiver
                    #update the users balance
                    users_balance_in +=  holding_transaction_outputs.amount

                    # no input_ref has been spent in a previous block on this chain [test_doublespent_input_same_chain]
                    # (you may find nonempty_intersection and chain.blocks_spending_input helpful here)
                    #checks that the blocks on the chain dont intersect with the blocks already spent for the input reference given
                    #solves the fork problem
                    if blockchain.util.nonempty_intersection(blocks_on_chain, chain.blocks_spending_input.get(ref, [])):
                         # On failure: return False, "Double-spent input"
                        return False, "Double-spent input"
                    
                   # (or in this block; you will have to check this manually) [test_doublespent_input_same_block]
                    for other_tx in self.transactions:
                        if other_tx != tx:
                            for references in other_tx.input_refs:
                                if references == ref:
                                    return False, 'Double-spent input'
                        
                            
                    # (or in this block; you will have to check this manually) [test_input_txs_in_block]
                    # (you may find chain.blocks_containing_tx.get and nonempty_intersection as above helpful)
                    # On failure: return False, "Input transaction not found"
                    inputRefInBlock = False
                    if blockchain.util.nonempty_intersection(blocks_on_chain, chain.blocks_containing_tx.get(tx_hash, [])):
                        inputRefInBlock = True
                    
                    for other_tx in self.transactions:
                        for references in other_tx.input_refs:
                                if other_tx.hash == tx_hash:
                                    inputRefInBlock = True
                    if not inputRefInBlock:
                        return False, 'Input transaction not found'

                user_balance_out = 0
                for output in tx.outputs:
                    # every output was sent from the same user (would normally carry a signature from this user; we leave this out for simplicity)
                    # (this MUST be the same user as the outputs are locked to above) [test_user_consistency]
                    # On failure: return False, "User inconsistencies"
                    #The sender of the next transaction must be the user and not someone else
                    if (output.sender != user):
                        #print('User Output consistency: Expected ', user, 'to be the sender but instead got ', output.sender)
                        return False, "User inconsistencies"
                    user_balance_out += output.amount
                
                # the sum of the input values is at least the sum of the output values (no money created out of thin air) [test_no_money_creation]
                # On failure: return False, "Creating money"
                if user_balance_out > users_balance_in:
                    return False, "Creating money"

        return True, "All checks passed"


    # ( these just establish methods for subclasses to implement; no need to modify )
    @abstractmethod
    def get_weight(self):
        """ Should be implemented by subclasses; gives consensus weight of block. """
        pass

    @abstractmethod
    def calculate_appropriate_target(self):
        """ Should be implemented by subclasses; calculates correct target to use in block. """
        pass

    @abstractmethod
    def seal_is_valid(self):
        """ Should be implemented by subclasses; returns True iff the seal_data creates a valid seal on the block. """
        pass



