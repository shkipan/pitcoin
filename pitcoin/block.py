import sys, hashlib
from merkle import merkle_root
from time import time
from tx_validator import validate_raw
from serializer import Deserializer
import struct

max_nonce = 2 ** 32

class Block():

    def __init__(self, tm, non, ph, transs):
        self.timestamp = tm
        self.nonce = non
        self.previous_hash = ph
        self.transactions = transs
        self.mroot = merkle_root(transs)
        self.version = 47
        self.target = 2 ** (256 - 1)
        self.heigth = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        v = struct.pack('<L', 1).hex()
        ts = str(self.timestamp)
        tar = hex(self.target)
        no = struct.pack('<L', self.nonce).hex()
        res = v + self.previous_hash  + self.mroot + ts + tar + no
        hsh = hashlib.sha256(bytes(res, 'utf-8')).hexdigest()
        self.hash = hsh
        return (hsh)
    
    def validate(self, prev_blocks, utxo):
        if (len(prev_blocks) > 0):
            ts_avg = 0
            for i in prev_blocks:
                ts_avg += i.timestamp
            ts_avg = ts_avg / len(prev_blocks)
            if (self.timestamp < ts_avg):
                print ('Invalid timestamp')
                return False
        for item in self.transactions:
            x = Deserializer.deserialize_raw(item)
            if not validate_raw(utxo, x):
                return False
        return True
    
if __name__ == '__main__':
    x = Block(1550301281.172262, 21,  '0', [str(i) for i in range(9)])
    print (x.calculate_hash())

