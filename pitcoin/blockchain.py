import sys, hashlib


max_nonce = 2 ** 32

class Blockchain():


    def __init__(self):
        self.complexity = 2

    def mine(self, bl):
 #       difficulty = 2 ** (256 - self.complexity * 4)
        for nonce in range(max_nonce):  
            sha = hashlib.sha256(bytes(str(bl.header) + str(nonce), 'utf-8')).hexdigest()
  #          if int(sha, 16) < difficulty:
            if sha[0:2] == '0' * self.complexity:
                print ('nonce = ', nonce)
                print ('hash is ',  sha)
                bl.nonce = nonce
                return (nonce)
        print ('failed to find')
        bl.nonce = -1
        return (-1)
