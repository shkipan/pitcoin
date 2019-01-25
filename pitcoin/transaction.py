import sys, hashlib, binascii

class Transaction():
    
    def __init__(self, s, r, a):
        self.sender = s
        self.recipient = r
        self.amount  = a
        self.signature = ''
        self.public_address = ''

    def gethash(self):
        s = self.sender + self.recipient + str(hex(self.amount)).replace('0x', '')
        h = hashlib.sha256(bytes(s, 'utf-8')).hexdigest().upper()
        return (h)

    def display(self):
        print ('Transaction info')
        print ('\tsender:   ', self.sender)
        print ('\trecipient:', self.recipient)
        print ('\tamount:', self.amount)

class CoinbaseTransaction(Transaction):
    def __init__(self, s):
        self.sender = '0'*34
        self.recipient = s
        self.amount  = 50
        self.signature = ''
        self.public_address = ''


