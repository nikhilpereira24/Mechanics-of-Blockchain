from typing import Optional, List
from hashlib import sha256
import numpy as np

def verify(obj: str, proof: str, commitment: str) -> bool:
    proof_list = proof.split(',') #split the path by the comma seperator
    if proof_list[0] == obj and proof_list[-1] == commitment: #check that the first element is the object and the last element is the root
        return True
    else:
        return False
    
class Prover:
    def __init__(self):
        self.objects = []
        self.tree = {}

    # return the hash of a string
    def SHA(self,s):
        return sha256(s.encode()).hexdigest()

    # Build a merkle tree and return the commitment
    def build_merkle_tree(self, objects: List[str]) -> str:
        def buildTreeRec(nodes):
            half = len(nodes) // 2
            if len(nodes) == 2: #base case once we reach two leaves, set the key of this node equal to the Hash of the combined nodes
                self.tree[nodes[0]] = self.SHA(nodes[0] + nodes[1]) 
                self.tree[nodes[1]] = self.SHA(nodes[0] + nodes[1])
                return self.SHA(nodes[0] + nodes[1]) #return the hash of the combine nodes

            left = buildTreeRec(nodes[:half]) #build the left subtree
            right = buildTreeRec(nodes[half:]) #build the right subtree
            self.tree[left] = self.SHA(left + right) #sets the left non-leaf node equal to the has of the left and right non-leaf nodes
            self.tree[right] = self.SHA(left + right) #sets the right non-leaf node equal to the hash of the left and right non-leaf nodes
            return self.SHA(left + right) #returns the commitment hash

        def NextPowerOfTwo(number):
        # Returns next power of two following 'number'
            return int(2**np.ceil(np.log2(number)))
        #Created another object list
        self.objects = objects
        while len(self.objects) != NextPowerOfTwo(len(objects)): #Add to the list until a power of 2 leaves in the tree
            self.objects.append('#') #append a marker #
        ls = []
        for x in self.objects: #append the hash of each object 
            ls.append(self.SHA(x))

        self.tree['Root'] = buildTreeRec(ls) #set the root of the tree equal to the recursive functions output
        return self.tree['Root'] #return the commitment

    def get_leaf(self, index: int) -> Optional[str]:
        # Complete the Prover.get leaf method that returns
        # the object at the particular leaf index. Note that index starts from 0, left to right. Return None if
        # there is no object at the given index
        # Return the index of the leaf if its less than the length and not marked as a '#' denoting fake leaves
        if index < len(self.objects) and self.objects[index] != '#': 
            return self.objects[index]
        else:
            return None

    def generate_proof(self, index: int) -> Optional[str]:
        #Function that traverses the dictionary of key value pairs all the way from the leave to the root
        def getPath(finalTree, leaf):
            traversing = True
            rootValue = finalTree['Root']
            path = [] #appends the traversal path from leaf to root
            path.append(leaf)
            currentKey = self.SHA(leaf) #start current key with the hash of the leaf and update in while loop
            while traversing:
                path.append(currentKey)
                if currentKey in finalTree.keys():
                    if finalTree[currentKey] == rootValue:
                        traversing = False
                    else:
                        currentKey = finalTree[currentKey]
                else:
                    return None
            path.append(rootValue)
            return ",".join(path) #return as a string joined by commas
        leaf = self.get_leaf(index)
        if leaf is None:
            return None
        return getPath(self.tree,leaf)

## Test code to verify that a root exists for all leaves and doesnt exist for non leaf index
objects = ['a','b','c','d','e','f','g','h','i'] #list of objects
prove = Prover() #instantiate the class
leaf_index = 2 #set a leaf index to test
prove.build_merkle_tree(objects) #build the merkle tree
object_to_check = prove.get_leaf(leaf_index) #get the leaf object
path = prove.generate_proof(leaf_index) #generate the proof path
commitment = prove.tree['Root'] #set the commitment
if path:
    print('Is Valid Path', path)
    print('Object',path.split(',')[0]) 
    print('End Path Value', path.split(',')[-1])
    print('Commitment of Tree', commitment)
    print(verify(object_to_check,path,commitment)) #verify that the path and the commitment match and verify function returns true
else:
    print("Path is ", path, "at given index") #this path is not possible given index set
