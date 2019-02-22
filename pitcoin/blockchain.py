import sys, hashlib
import json, requests, urllib.request, random
import wallet
from time import time
from transaction import CoinbaseTransaction, Transaction
from serializer import Serializer, Deserializer
from block import Block
from merkle import merkle_root
from wallet import *
from utxo_set import *
from tx_validator import *
from operator import itemgetter
import threading

from syncdata import get_config
from pathlib import Path

#home = str(Path.home()) + '/.pitcoin/'
home = './.pitcoin/'
my_url, PORT = get_config()
PORT = str(PORT)

max_nonce = 2**32

class Blockchain():

    def mine(self, bl):
        bl.target = self.target
        for nonce in range(max_nonce):
            bl.nonce = nonce
            bl.hash = bl.calculate_hash()
            if int (bl.hash, 16) < self.target:
#            if bl.hash[0:self.complexity] == '0' * self.complexity:
                if not self.muted:
                    print ('nonce = ', nonce)
                    print ('hash is ',  bl.hash)
                return 1
        bl.timestamp = time()
        mine(bl)
        return 1

    def create_gen_block(self, file_name):
        try:
            addr = open(file_name, 'r').readline().replace('\n', '')
        except IOError:
            if not self.muted:
                print ('No file', file_name)
            sys.exit()
            return None
        privk = wallet.convert_from_wif(addr)
        publa = wallet.get_public_address(privk)
        cbtrans = CoinbaseTransaction(publa, self.reward)
        cbserial = Serializer.serialize_raw(cbtrans, '', '').hex()
        bl = Block(time(), 0, '0', [cbserial])
        bl.target = self.target
        self.mine(bl)
        return (bl)

    def premine(self):
        random.seed(time())
        privkey = [get_new_private_key() for i in range(3)]
        publkey = [get_public_key(privkey[i]) for i in range(3)]
        addr = [get_public_address(privkey[i]) for i in range(3)]
        for i in range(len(privkey)):
            item = privkey[i]
            with open('premine' + str(i), 'w+') as f:
                f.write(convert_to_wif(item))
        for i in range(len(addr)):
            bl = self.create_gen_block('premine' + str(i))
            if bl:
                if len(self.blocks) > 0:
                    bl.previous_hash = self.blocks[len(self.blocks) - 1].hash
                bl.heigth = len(self.blocks)
                bl.previous_hash = self.last_hash
                bl.target = self.target
                self.mine(bl)
                self.blocks.append(bl)
                self.last_hash = bl.hash
        utxo = []
        for i in self.blocks:
            trans = Deserializer.deserialize_raw(i.transactions[0])
            utxo_add(utxo, trans)
        for x in range(3):
            for ind in range(len(addr)):
                for jnd in range(len(addr)):
                    i = addr[ind]
                    j = addr[jnd]
                    if i != j:
                        amount = random.randint(6, 15)
                        if not self.muted:
                            print (i, j, amount)
                        inputs = utxo_select_inputs(utxo_get(utxo, i), 5, amount)
                        outputs = utxo_create_outputs(i, j, amount, 5, inputs)
                        if len(inputs) == 0:
                            continue
                        tr = Transaction(i, j, amount, {'inp': inputs, 'oup': outputs, 'locktime':0, 'version': 1})
                        tr_serial = Serializer.serialize_raw(tr, privkey[ind], publkey[ind])
                        tr_des = Deserializer.deserialize_raw(tr_serial.hex())
                        utxo_add(utxo, tr_des)
                        bl = Block(time(), 0, self.last_hash, [tr_serial.hex()])
                        bl.target = self.target
                        self.mine(bl)
                        bl.heigth = len(self.blocks)
                        self.blocks.append(bl)
                        self.last_hash = bl.hash

        #deleting premine files
        '''
        for i in range(len(privkey)):
            if os.path.isfile('premine' + str(i)):
                os.remove('premine' + str(i))
        '''
  
    def __init__(self, premine=False, muted=True):
        self.last_hash = '0'        
        self.muted = muted
        self.blocks = []
        self.complexity = 16
        self.target = 2 ** (256 - self.complexity)
        self.reward = 50
        if premine:
            return self.premine()
        data = {}
        try:
            with open(home + 'blockchain', 'r') as f:
                tex = f.read()
                data = json.loads(tex)
        except FileNotFoundError:
            if not self.muted:
                print ('No blockchain file!')
        except json.decoder.JSONDecodeError:
            if not muted:
                print ('Invalid file')
        if (len(data) != 0):
            if not muted:
                print ('Blockchain file opened')
            for i in data:
                bl = Block(i['timestamp'], i['nonce'], i['previous_block_hash'], i['transactions'])
                bl.mroot = i['merkle_root']
                bl.heigth = i['heigth']
                bl.target = i['target']
                bl.calculate_hash()
                self.blocks.append(bl)
                self.last_hash = bl.hash
        else:
            bl = self.create_gen_block('miners_key')
            bl.target = self.target
            self.mine(bl)
            self.blocks.append(bl)
            self.last_hash = bl.hash

    def is_valid_chain(self, utxo):
        item = [x for x in self.blocks if x.hash == self.last_hash]
        if (len(item) == 0):
            print ('wrong last hash')
            return False
        item = item[0]
        while (True):
            if int (item.hash, 16) > self.target:
                print ('wrong number of zeros in hash')
                return False  
            test_hash = item.calculate_hash()
            if (test_hash != item.hash):
                print (item.hash, test_hash)
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
        for i in range(len(self.blocks)):
            bl = self.blocks[i]
            bldiapp = self.blocks[i - 3: i] if  i > 2 else []
            if not bl.validate(bldiapp, utxo):
                return False
        if not self.muted:
            print ('Blockchain is valid')
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

