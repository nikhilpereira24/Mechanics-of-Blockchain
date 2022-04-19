from importlib.resources import path
from pathlib import Path
import string
import random
import hashlib
import numpy as np
from essential_generators import DocumentGenerator

# return the hash of a string
def SHA(s: string) -> string:
    return hashlib.sha256(s.encode()).hexdigest()

# transfer a hex string to integer
def toDigit(s: string) -> int:
    return int(s, 16)

# generate 2^d (si^{-1}, si) pairs based on seed r
def KeyPairGen(d: int, r: int) -> dict:
    pairs = {}
    random.seed(r)
    for i in range(1 << d):
        cur = random.randbytes(32).hex()
        while cur in pairs:
            cur = random.randbytes(32).hex()
        pairs[cur] = SHA(cur)
    return pairs


class MTSignature:
    def __init__(self, d, k):
        self.d = d
        self.k = k
        self.treenodes = [None] * (d+1)
        for i in range(d+1):
            self.treenodes[i] = [None] * (1 << i)
        self.sk = [None] * (1 << d)
        self.pk = None # same as self.treenodes[0][0]

    # Populate the fields self.treenodes, self.sk and self.pk. Returns self.pk.
    def KeyGen(self, seed: int) -> string:
        def getTree(objects): #creates a nested lists of tree nodes
            def NextPowerOfTwo(number): #finds the next power of two for any number
                return int(2**np.ceil(np.log2(number)))
            def SHA(s): #sha function
                return hashlib.sha256(s.encode()).hexdigest()
            while len(objects) != NextPowerOfTwo(len(objects)): #pad objects less than a power of 2
                objects.append((''))
            objects = [(i, x) for i, x in enumerate(objects)] #store the index of each leaf
            gl = [objects] #global list appends leaf objects
            traverse = True
            objects = [x[1] for x in objects] #just keep objects as the values not index
            while traverse:
                i=0
                level = []
                count=0
                while i < len(objects)-1: #for each level, store the index and the binary representation + object i + object i + 1
                    level.append((count,SHA('{:0256b}'.format(count)+objects[i]+objects[i+1])))
                    i+=2 #skip to the next pair
                    count+=1 #update count index (the index in level)
                gl.append(level) #global list adds the level
                objects = [x[1] for x in level] #next set of objects is just the hash value not indices (for iteration purposes)
                if len(level) == 1: #once reached the root
                    traverse=False
            return list(reversed(gl)) #return the tree in reverse order to be stored in tree nodes

        pairs = KeyPairGen(self.d,seed) #obtain the pairs from key pair gen function
        self.sk = list(pairs.keys()) #set the private keys
        treeList = getTree(list(pairs.values())) #get the built merkle tree implemented as nested arrays
        for i,level in enumerate(treeList): #iterate the tree list and set the treenodes appropriately
            for node in level:
                self.treenodes[i][node[0]] = node[1]
        self.pk = self.treenodes[0][0] #set the public key to be the root node
        return self.pk #return the public key
    # Returns the sgnature. The format of the signature is as follows: ([sigma], [SP]).
    # The first is a sequence of sigma values and the second is a list of sibling paths.
    # Each sibling path is in turn a d-length list of tree node values. 
    # All values are 64 bytes. Final signature is a single string obtained by concatentating all values.
    def Sign(self, msg: string) -> string:
        #gets the sibling path for the element
        def getPath(element):
            path = []
            for d,level in enumerate(list(reversed(self.treenodes))):
                if d == len(self.treenodes)-1: #if the depth is end depth of tree we are at the root
                    break
                else:
                    if element % 2 == 0: #even element
                        path.append(level[element+1]) #add its pair to the path
                        element = int(element/2) #the next non leaf node will be the element divided by 2
                    else: #odd node
                        path.append(level[element-1]) #add its even counterpart
                        element = int((element-1)/2) #next non leaf node will be the element - 1 / 2
            return "".join(path) #return the joint sibling path
        Sigma = ''
        Paths = ''
        for j in range(1,self.k+1):
            binRepresentation = (bin(j)[2:]).zfill(256) #binary representation of j
            concatMesg = str(binRepresentation) + msg #concatenated Message
            Zj = int(SHA(concatMesg),16) % (2**self.d) #formula for Zj
            Sigmaj = self.sk[Zj] #sigma j
            path = getPath(Zj) #get path for Zj
            Sigma += Sigmaj #append sigma j to sigma
            Paths += path #append path to list of paths
        return str(Sigma) + str(Paths) #concatenate the sigma and path == signature


    def findForgedSignature(self,message,k):
        signature_sigma = self.Sign(message)[:k*64] #get the first k*64 bits of signature equaling the sigma
        foundForge = False
        i=0
        while not foundForge:
            #generate random names
            names=["Jack","Jim",'Nikhil','Ari','Nick','John','Joe','Julia','Michael','Martin','Matthew']
            #generate random verb
            setup = ['made', 'won','lost']
            #generate random number
            number = random.randint(1, 10000)
            #generate random ending
            end = ['yesterday.','today.','last week.','last month.','last year.','last century.']
            a=(random.choices(names))
            b=(random.choices(setup))
            d=(random.choices(end))
            # Number + is how much + Name + Verb + Ending
            m_prime = str(number) + ' is how much ' + " ".join(a+b+d)
            new_sigma = self.Sign(m_prime)[:k*64]
            if new_sigma == signature_sigma: #check they're the same
                print('Alternate Sigma', new_sigma)
                foundForge = True #break loop
            i+=1
        print('Num Iterations to find', i)
        return m_prime #return the alternate message


#Test Cases
S1 = MTSignature(2, 1)
S1.KeyGen(1)
assert(S1.KeyGen(1) == "9847bdbabc1d8b0b930db4e41f425a48dbd5bf8be82d6ad006d099827d0d26a7")
testcase1 = "8c2e0718822ce47ca8c74107e66cb0e4b2b3f4d58d82ca6386d2c96e760e819b3dd4009946ba3b8b04d533d723c166fa90fdff0ef116869c4af946b6181877414ae6eceab43f19e2688fbca9cac19515212004edbe671dd8cc9256ed93f18617"
print("My Result signature length", len(S1.Sign("I Love 5433")), "Length of testcase signature", len(testcase1))
print(S1.Sign("I Love 5433") == testcase1)

S2 = MTSignature(10, 3)
testcase2 = "b2c859c8fe6bf62390a6ad709060b03792d3b6275f2ec8e65fcceb634ef53b71fa5ee86a8e23c78d0401e92a25ede9b287713e65f8d8d3b2dd579b63f6bdf1ce236f8fef896d0284310381b98e85b330a33e47b339120881ec1cccb0d654a39cfdb4f70abf9512601d03af9c6011fb234bffe3ccab6d4f00363d245dea15a3ba60eebc478ef71b9114b94b33209645fc79d0f4c1bf62cc6eaf645af49d0a171b04c37c1e7d77d776614d63e6867ad9b2316cd84dd678fe37611f03ede27d2a130e37d0282c751e56b4f528969b23d4c4cd2e3092b7a5d1f23edfdf66e4ea7617f54586a707ceae4163643d8cad1dbc23a45868abef8699f534e1baedfd64e56fb5496438b2df390c4696870a4c944fc6bb2695729089281c597ed14fc83720fcb25f6a62894e937d1e8d7e93dc249be3f877f128e0fb882955568aef736880ce563996be24bb937d1d91faf73ccb9d120dbbbbad12a075dbc61b9e8a6bc1e28fc5ff2c9502e24a4d47dda9e9c347c28981654464932605faa163c46286c3313e9e7cc4a630ebb47b299d6ae7231f7a1e6665e8ad1c2352427ae8eef6229a5e16114f7c8945fa68fd984334892bab6714753db064897406517ae2f67c9a77f962bdf1ad5df006fdc85cb34ded12c368b74af510ee1024d0d77fb0faa184d72226bd06fda5a2e889b04dc08dd0b43a9b795147f0c9cf938305c11bb67a018993495601930a0328980bf698469ea96065a9133a0b24528e4e4d6ee15a7810a35a1ccebe9705643b595b64b03c052d43e041661c7ee8ee78a646c2a013774e9b02347a06739578de93049228a21cbd317ea430e666b0b49452758d71f5f8e2c2b192e4331d740ac9459e6953f197a2dc6d873829b61c3ad08acb6520850d08da771c33c18e8c9e3c81b5bc91a27c374422a0245969c064e8e6661b4bdbe33b468d06ee3915b5987a181afc159b4f2532937bbe3d1b1a1b1d3207f022f69a1cfe286a4c6f5b865841dd2ab4bf5103eb69cf4ec71f78fc26ccbb9b44b432d9616eb6755b1887d2a24f98443cebf8ff502f076c631b3a9bdf2576c369ee760f1ee2b8d37813ca38587d618fe397174b3361e813d92506881a6c06903c4cb71aad3519fa194d54b4e95180b2f6750eb429cfdcf643fd36617a2b6781b60b31dd01c1a2308c66c1dc59dc5e4e684b0f39e279ec05b93904bac5e059b1312caf9fe288c775d5b06b32a1e84734fd50dc41a191ca8e1246bdede40e0aa5ec0dbb5ae57a67ffbd245bead30fea34ab21562bf7735a5b2f4addf7328a22f0c4f914ef620e89baec04224e967f1b0c2e7012489721408f76d577ca70408f196339ed05e0f61b6c33c18e8c9e3c81b5bc91a27c374422a0245969c064e8e6661b4bdbe33b468d06ee3915b5987a181afc159b4f2532937bbe3d1b1a1b1d3207f022f69a1cfe286a4c6f5b865841dd2ab4bf5103eb69cf4ec71f78fc26ccbb9b44b432d9616eb675"
assert(S2.KeyGen(1) == "f1f3bfb5a76332fdf292a35195a33ad1b0c28621b044afd00d6ffa359d19cb05")
print("My Result signature length", len(S2.Sign("I Love 5433")), "Length of testcase signature", len(testcase2))
print(S2.Sign("I Love 5433") == testcase2)
assert(S2.Sign("I Love 5433") == testcase2)

S3 = MTSignature(10, 2)
r = 2022
m = '5433 is my favorite number'
S3.KeyGen(r)
print('Message Sigma',S3.Sign(m)[:128])
m_prime = S3.findForgedSignature(m,2)
print('Forged Signature',m_prime,  S3.Sign(m_prime) == S3.Sign(m))
assert(S3.Sign(m_prime) == S3.Sign(m))