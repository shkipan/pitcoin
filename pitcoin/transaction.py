import sys, hashlib, binascii, struct

#for test
import time

class Transaction():
    
    def __init__(self, s, r, a, ext):
        self.sender = s
        self.recipient = r
        self.amount  = a
        self.signature = ''
        self.public_address = ''

        if not ext:
            return 
        self.version = ext['version'] 
        self.inputs = ext['inp']
        self.outputs = ext['oup']
        self.inputs_num = len(ext['inp'])
        self.outputs_num = len(ext['oup'])
        self.timelock = ext['locktime']
        self.tr_hash = ''

    def gethash(self):
        s = self.sender + self.recipient + str(hex(self.amount)).replace('0x', '')
        h = hashlib.sha256(bytes(s, 'utf-8')).hexdigest().upper()
        return (h)

    def display(self):
        print ('Transaction info')
        print ('\tsender:   ', self.sender)
        print ('\trecipient:', self.recipient)
        print ('\tamount:', self.amount)
        print ('\tsignature:', self.signature)

    def display_raw(self):
        print ('__________________________________________')
        print ('transaction hash:', self.tr_hash.hex())
        print ('version:   ', binascii.hexlify(struct.pack('<L', self.version)).decode()) 

        print ('input count:', binascii.hexlify(struct.pack('<L', len(self.inputs))).decode())
        print ('output count:', binascii.hexlify(struct.pack('<L', len(self.outputs))).decode())
        for i in self.inputs:
            print ('input:')
            print (i)
        for i in self.outputs:
            print ('output:')
            print (i)
        print ('timelock:', self.timelock, 'blocks' if self.timelock < 500000000 else 'seconds', '|{:08x}|'.format(self.timelock))
        print ('__________________________________________')

class CoinbaseTransaction(Transaction):
    def __init__(self, s):
        self.sender = '0'*34
        self.recipient = s
        self.amount  = 50
        self.signature = ''
        self.public_address = ''

if __name__ == '__main__':
    print ()
