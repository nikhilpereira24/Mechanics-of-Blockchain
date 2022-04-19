import blockchain
from blockchain.block import Block
from blockchain.util import nonempty_intersection

class PoWBlock(Block):
    """ Extends Block, adding proof-of-work primitives. """

    def seal_is_valid(self):
        """ Checks whether a block's seal_data forms a valid seal.
            In PoW, this means that H(block) <= target

            Returns:
                bool: True only if a block's seal data forms a valid seal according to PoW.
        """
        return int(self.hash, 16) <= self.target

    def get_weight(self):
        """ Gets the approximate total amount of work that has gone into making a block.
            The consensus weight of a block is how much harder a block is to mine
            than the easiest possible block, with a target of 2^256.
            e.g. a block with weight 4 will take 4 times longer on expectation to mine than
            a block carrying target 2^256.
            Target should be within the range [1, 2^256]. For targets out of this range, return 0.

        Returns:
            int: The consensus weight of a block, rounded to integer.
        """

        # Placeholder for (1a)
        if 1 <= self.target <= 2**256:
            return 2**256 / self.target
        else:
            return 0

    def mine(self):
        """ PoW mining loop; attempts to seal a block with new seal data until the seal is valid
            (performing brute-force mining).  Terminates once block is valid.
        """
        nonce = 0
        while not self.seal_is_valid():
            self.set_seal_data(nonce)
            nonce += 1

    def calculate_appropriate_target(self):
        """ For simplicity, we will just keep a constant target / difficulty
        for now; in real cryptocurrencies, the target adjusts based on some
        formula based on the parent's target, and the difference in timestamps
        between blocks  indicating mining is too slow or quick. """
        if self.parent_hash == "genesis":
            return int(2 ** 248)
        return blockchain.chain.blocks[self.parent_hash].target
