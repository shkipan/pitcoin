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

    def display_raw(self):
        print ('__________________________________________')
        print ('transaction hash:', self.tr_hash.hex() if len(self.tr_hash) > 0 else '')
        print ('version:   ', self.version) 

        print ('input count:', self.inputs_num)
        print ('output count:', self.outputs_num)
        for i in self.inputs:
            print ('input:')
            print (i)
        for i in self.outputs:
            print ('output:')
            print (i)
        print ('timelock:', self.timelock, 'blocks' if self.timelock < 500000000 else 'seconds', '|{:08x}|'.format(self.timelock))
        print ('__________________________________________')

class CoinbaseTransaction(Transaction):
    def __init__(self, s, rew):
        self.sender = '0'*34
        self.recipient = s
        self.amount  = rew
        self.signature = ''
        self.public_address = ''

        ext = {'inp': [{'amount': rew, 'tx_prev_hash': '0'*64, 'tx_prev_index': 4294967295}], 
                'oup': [{'value': rew, 'address': s}], 
                'locktime': 0, 'version': 1}
        self.version = ext['version'] 
        self.inputs = ext['inp']
        self.outputs = ext['oup']
        self.inputs_num = len(ext['inp'])
        self.outputs_num = len(ext['oup'])
        self.timelock = ext['locktime']
        self.tr_hash = ''


if __name__ == '__main__':
    print ()
