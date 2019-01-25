import sys, hashlib
from merkle import merkle_root
from time import time
from tx_validator import verification
from serializer import Deserializer

class Block():

    def __init__(self, non, ph, transs):
        self.timestamp = time()
        self.nonce = non
        self.previous_hash = ph
        self.transactions = transs
        self.mroot = ''
        self.hsh = ''
        self.header = ''

    def calculate_hash(self):
        ts = str(self.timestamp)
        no = str(hex(self.nonce)).replace('0x', '')
        trans_hash = ''
        for i in self.transactions:
            #trans_hash += hashlib.sha256(bytes(i, 'utf-8')).hexdigest().upper()
            trans_hash += i
        res = ts + no + self.previous_hash + trans_hash + self.mroot
        self.hsh = hashlib.sha256(bytes(res, 'utf-8')).hexdigest().upper()
        return (self.hsh)
    
    def setup(self, trans):
        self.mroot = merkle_root(trans)
        self.calculate_hash()
        self.header = str(self.timestamp) + self.previous_hash + self.mroot + self.hsh
    
    def validate(self):
        for item in self.transactions:
            x = Deserializer.deserialize(item)
            if not verification(x):
                return False
        return True

if __name__ == '__main__':
    x = Block(0, '0', [str(i) for i in range(9)])
    print (x.calculate_hash())

