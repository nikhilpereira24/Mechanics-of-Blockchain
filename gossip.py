
import sys
import os
# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))
  
# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)
  
# adding the parent directory to 
# the sys.path.
sys.path.append(parent)

import config
import requests
import importlib
from p2p import synchrony
from p2p.interfaces.block import string_to_block
from blockchain.util import run_async

@run_async
def send_message(dest, type, message):
    """ Send message to destination node over point-to-point network.

        Args:
            dest (str): IP address of receiver.
            type (str): Type of message to process as; unknown types are ignored.
            message (str): Payload to deliver to destination to be processed based on type.
    """
    try:
        print(requests.post(dest + "p2pmessage/" + type + "/" + str(config.receiving_port), data=str(message), timeout=2).text)
    except Exception as e:
        print("[p2p error] Message failed to send to", dest)
        print(e)

def gossip_message(type, message):
    """ Send message to all known nodes over point-to-pont network (broadcast).

        Args:
            type (str): Type of message to process as; unknown types are ignored.
            message (str): Payload to deliver to destination to be processed based on type.
    """
    # (you should use send_message as a primitive; also see the config file)
    if config.node_id == 0: #if the nodes id is default send message to whole network
        for dest in config.PEERS.values():
            send_message(dest, type, message)
    else:
        for node,dest in config.PEERS.items():
            if node != config.node_id:
                send_message(dest, type, message)

    # (placeholder for 3.1)
    # implement here


def handle_message(type, message, sender):
    """ Used to handle an incoming message sent by another node (heh-heh-heyyyy!).

        Args:
            type (str): Type of message to process as; unknown types are ignored.
            message (str): Payload to deliver to subcomponent based on type.
            sender (str): Sender of message (primarily used to find key in PKI).
    """
    print("SENDER", sender)

    if type == "addblock":
        # Add block to blockchain
        block = string_to_block(message)
        from blockchain import chaindb
        chaindb.connection.close()
        chaindb.db.close()
        importlib.reload(chaindb)
        chain = chaindb.chain
        #print(block)
        print(block.is_valid())
        if not block.hash in chain.blocks and block.is_valid()[0]:
            # if it's a valid block we haven't seen, retransmit
            chain.add_block(block)
            gossip_message(type, message)
        chaindb.connection.close()
        chaindb.db.close()

    if type == "synchrony-start":
        # Kick off the round-based synchrony tracker
        if not synchrony.is_started():
            synchrony.receive_start_message()
            gossip_message(type, "")

    if type == "ba-start":
        # Kick off the BA protocol
        if config.ba == None:
            from byzantine_agreement.simple_ba import SimplePKIBA
            from byzantine_agreement.byzantine_ba import ByzantineSimplePKIBA
            if not config.node_id in config.BYZANTINE_NODES:
                config.ba = SimplePKIBA(config.sender)
            else:
                config.ba = ByzantineSimplePKIBA(config.sender)
            gossip_message(type, message)

    if type == "ba-vote":
        # Send confirmed vote to our BA protocol
        config.ba.process_vote(message)

