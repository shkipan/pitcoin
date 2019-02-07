import sys, hashlib
from merkle import merkle_root
from time import time
from tx_validator import verification
from serializer import Deserializer

max_nonce = 2 ** 32

class Block():

    def __init__(self, tm, non, ph, transs):
        self.timestamp = tm
        self.nonce = non
        self.previous_hash = ph
        self.transactions = transs
        self.mroot = merkle_root(transs)
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        ts = str(self.timestamp)
        no = str(self.nonce)
        trans_hash = ''
        for i in self.transactions:
            trans_hash += hashlib.sha256(bytes(i, 'utf-8')).hexdigest().upper()
        res = ts + no + self.previous_hash + trans_hash + self.mroot
        hsh = hashlib.sha256(bytes(res, 'utf-8')).hexdigest().upper()
        return (hsh)
    
    def validate(self):
        for item in self.transactions:
            x = Deserializer.deserialize(item)
            if not verification(x):
                return False
        return True
    
if __name__ == '__main__':
     x = Block(time(),0,  '0', [str(i) for i in range(9)])
     x.mine(2)
     print (x.calculate_hash())

