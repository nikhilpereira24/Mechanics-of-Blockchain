from hashlib import sha256
import numpy as np
import random 
import string

def encodeASCII(string):
    encodedID = string.encode('ascii','replace')
    return encodedID

def hash256asHex(string):
    hashed = sha256(string).hexdigest()
    return hashed

def convertHexToBinary(my_hexdata,num):
    res = (bin(int(my_hexdata, 16))[2:]).zfill(256)
    x = res[0:num]
    return x

def convert(string, numCharacters):
    encoded = encodeASCII(string)
    hashed = hash256asHex(encoded)
    first_X = convertHexToBinary(hashed, numCharacters)
    return first_X

def SHA(s):
    return sha256(s.encode()).hexdigest()


def generateCoin(watermark):
    c_random = random.randbytes(8).hex() #generate a 64 bit string as hex 
    bits = (bin(int(c_random,16))[2:]).zfill(64) #convert to bits
    coin_bin = str(watermark) + str(bits) #concatenate the watermark with the bits
    coin_bin = coin_bin[:64] #keep the first 64
    coin_hex = (hex(int(coin_bin,2))[2:]).zfill(16) #convert to hex
    output_d = sha256(bytes.fromhex(coin_hex)).digest() #call the hash function
    output_d_bin = (bin(int.from_bytes(output_d,'big'))[2:]).zfill(256)
    return coin_hex, output_d_bin[:28] #return the coin in hex and its output in binary

def mintCoins(watermark):
    seen = {}
    k=4
    while True:
        coin, testHash = generateCoin(watermark)
        if testHash in seen.keys():
            seen[testHash].append(str(coin))
            if len(seen[testHash])==k:
                coins = seen[testHash]
                break
        else:
            seen[testHash] = [str(coin)]
    return coins

def printBits(coins):
    for c in coins:
        hex_coin = sha256(bytes.fromhex(c)).hexdigest()
        print(convertHexToBinary(hex_coin,28))


def generateRandomWatermark():
    alternateID = []
    for x in range(random.randint(2,3)):
        alternateID.append(random.choice(string.ascii_lowercase))
    for x in range(random.randint(1,10)):
        alternateID.append(str(random.randint(1,10)))
    alt_netID = "".join(alternateID)
    alternateWatermark = convert(alt_netID,10)
    return alternateWatermark, alt_netID

def forgeWaterMark(watermark):
    while True:
        alternateWatermark, altID = generateRandomWatermark()
        if alternateWatermark == watermark:
            print(alternateWatermark, watermark, altID, netID)
            return alternateWatermark

netID = 'nmp54'
encoded = encodeASCII(netID)
hashed = hash256asHex(encoded)
watermark = convertHexToBinary(hashed,10)
print('Watermark in Binary', watermark)
coins = mintCoins(watermark)
print('Set of Minted Coins', coins)
alternateWM = forgeWaterMark(watermark)
print('Alternate Watermark', alternateWM)