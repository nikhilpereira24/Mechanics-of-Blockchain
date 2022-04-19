# BlockchainCryptoSmartContracts

Course assignements for CS5431 Blockchains, Cryptocurrencies, and Smart Contracts taugh by Ari Juels at Cornell Tech. 

Course covers topics Bitcoin, Basic Crypto: Hash Functions, Public-Key Cryptography, Transactions/Scripts, Byzantine Agreement, Bitcoin Mining, Permissionless Consenses (Nakamoto Consensus), Proof of Stake, Wallets and Key Management, Privacy in Cryptocurrencies, Smart Contracts, Zero Knowledge Proofs, Privacy Coins, Oracles, DeFi: DEXes, Miner Extractable Value, Criminal SC's and Pyramid Schemes, NFT's, Decentralized Identity

### Homework 1 - Intro to Basic Crypto

Q1. Intro to Hash Functions

Became intimate with Hash Functions and generated my own currency Micromint in generateCoins.py

Q2. Intro to Merkle Trees

Built a merkle tree in merkle.py implemented as a complete binary tree so commitments can be verified as root node

Files: merkle.py

Q3. Intro into Digital Signature Schemes

Explored a hash-based signature scheme to sign and verify messages. KeyGen, Sign, Signature Forgery and Double signatures are explored

Files: signature.py and test.py

## Homework 2 

Q1. Signatures, Hashing, Sealing

Implemented a Proof Of Work algorithm to verify valid blocks
Implemented a Proof of Authority algorithm to mine blocks

Files: block.py, chain.py, poa_block.py, pow_block.py, utily.py

Q2. Exploring UTXO Management in Wallets

Understanding potential vulnerabilities in UTXO systems and identifying solutions. 

Q3. Peer 2 Peer Networks

Explored and implemented a P2P network to broadcast blockchain information over a network

Files: gossip.py

## Homework 3

Q1. Tokens and Simple Smart Contracts

Implements an ERC20 withdraw function to get familiar with Solidity coding. Deployed Smart Contract on a test network to verify functionality

Files: ERC20.sol

Q2. Gaming Contracts

Implemented a strategy to defeat monster on EtheremonLite contract. Explored and understood vulnerabilities created with public smart contracts

Files: winBattle.sol

Q3. Anonymity with Tumblers and Mixers?

Deanonymized users on the BTC network by mapping inputs to outputs from a mixing service. Discussed the cons with mixing services in cryptocurrencies.












