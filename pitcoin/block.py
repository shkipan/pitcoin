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
        self.hash = self.calculate_hash()
        self.heigth = 0

    def calculate_hash(self):
        v = struct.pack('<L', 1).hex()
        ts = str(self.timestamp)
        no = str(self.nonce)
        trans_hash = ''
        for i in self.transactions:
            trans_hash += hashlib.sha256(bytes(i, 'utf-8')).hexdigest()
        res = v + self.previous_hash + trans_hash + self.mroot + ts + no
        hsh = hashlib.sha256(bytes(res, 'utf-8')).hexdigest()
        return (hsh)
    
    def validate(self, prev_blocks, utxo):
        ts_avg = 0
        for i in prev_blocks:
            ts_avg += i.timestamp
        ts_avg = int(ts_avg / len(prev_blocks))
        if (self.timestamp < ts_avg):
            print ('Invalid timestamp')
            return False
        for item in self.transactions:
            x = Deserializer.deserialize_raw(item)
            if not validate_raw(utxo, x):
                return False
        return True
    
if __name__ == '__main__':
     x = Block(time(),0,  '0', [str(i) for i in range(9)])
     x.mine(2)
     print (x.calculate_hash())

