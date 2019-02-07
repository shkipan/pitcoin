import sys, hashlib
import json, requests, urllib.request
import wallet
from time import time
from transaction import CoinbaseTransaction
from serializer import Serializer, Deserializer
from block import Block
from merkle import merkle_root

from syncdata import get_config
from pathlib import Path

home = str(Path.home()) + '/.pitcoin/'
my_url, PORT = get_config()
PORT = str(PORT)

max_nonce = 2**32

class Blockchain():

    def mine(self, bl):
        for nonce in range(max_nonce):
            bl.nonce = nonce
            bl.hash = bl.calculate_hash()
            #print (nonce, bl.hsh)
            if bl.hash[0:self.complexity] == '0' * self.complexity:
#                print ('nonce = ', nonce)
#                print ('hash is ',  bl.hash)
                return
        bl.timestamp = time()
        mine(bl)

    def create_gen_block(self):
        try:
            addr = open('miners_key', 'r').readline().replace('\n', '')
        except IOError:
            print ('No miners_key file!')
            sys.exit()
            return None
        privk = wallet.convert_from_wif(addr)
        publa = wallet.get_public_address(privk)
        cbtrans = CoinbaseTransaction(publa)
        cbtrans.signature, cbtrans.public_address = wallet.sign(privk, cbtrans.gethash())
        cbserial = Serializer.serialize(cbtrans)
        bl = Block(time(), 0, '0', [cbserial])
        self.mine(bl)
        return (bl)

    def __init__(self):
        self.blocks = []
        self.complexity = 2
        data = {}
        try:
            with open(home + 'blockchain', 'r') as f:
                tex = f.read()
                data = json.loads(tex)
        except FileNotFoundError:
            print ('No blockchain file!')
        except json.decoder.JSONDecodeError:
            print ('Invalid file')
        if (len(data) != 0):
            print ('Blockchain file opened')
            for i in data:
                bl = Block(i['timestamp'], i['nonce'], i['previous_hash'], i['transactions'])
                bl.hash = i['hash']
                bl.mroot = i['mroot']
                self.blocks.append(bl)
                self.last_hash = bl.hash
        else:
            bl = self.create_gen_block()
            self.mine(bl)
            self.blocks.append(bl)
            self.last_hash = bl.hash

    def is_valid_chain(self):
        item = [x for x in self.blocks if x.hash == self.last_hash]
        if (len(item) == 0):
            print ('wrong last hash')
            return False
        item = item[0]
        while (True):
            if ('0' * self.complexity != item.hash[0:self.complexity]):
                print ('wrong number of zeros in hash')
                return False  
            test_hash = item.calculate_hash()
            if (test_hash != item.hash):
                print ('invalid hash of block')
                return False  
            test_mroot = merkle_root(item.transactions)
            if (test_mroot != item.mroot):
                print ('merlke root mismatch')
                return False  
            if (item.previous_hash == '0'):
                break
            item = [x for x in self.blocks if x.hash == item.previous_hash]
            if (len(item) == 0):
                print ('wrong prev hash')
                return False
            item = item[0]
        return True
        
    def chain_balance(self, addr):
        bal  = 0
        senders = []
        recipients = []
        for block in self.blocks:
            for trans in block.transactions:
                x = Deserializer.deserialize(trans)
                if x.sender == addr:
                    senders.append(x.amount)
                if x.recipient == addr:
                    recipients.append(x.amount)
        for i in recipients:
            bal += i
        for i in senders:
                bal -= i
        return bal

