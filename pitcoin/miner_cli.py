#!/usr/bin/env python
#wallet for creating transactions

import sys, cmd, os
import wallet, pending_pool
from wallet import termcolors
from block import Block
from serializer import Serializer, Deserializer
from transaction import CoinbaseTransaction
from merkle import merkle_root
from blockchain import Blockchain

class Shell(cmd.Cmd):
    prompt = termcolors.BLUE + 'miner-cli: ' + termcolors.DEF
    intro = "Pitcoin mining manager"

    def do_exit(self, line):
        print(termcolors.RED + 'Client stopped' + termcolors.DEF)
  #      if os.path.isfile('mempool'):
  #          os.remove('mempool')
        sys.exit()

    def preloop(self):
        return None
      #  if os.path.isfile('mempool'):
      #      os.remove('mempool')
      #  f = open('mempool', 'a')
      #  f.close

    def emptyline(self):
        return None

    def do_EOF(self, line):
        return True

    def do_help(self, line):
        wallet.print_help()

    def default(self, line):
        print ('### Unknown command: ' + line)
        print ('-' * len('*** Unknown command: ' + line))
        wallet.print_help()

    def do_mine(self, line):
        try:
            addr = open('miners_key', 'r').readline().replace('\n', '')
        except IOError:
            print ('No miners_key file!')
            return False
        privk = wallet.convert_from_wif(addr)
        publa = wallet.get_public_address(privk)
        cbtrans = CoinbaseTransaction(publa)
        cbtrans.signature, cbtrans.public_address = wallet.sign(privk, cbtrans.gethash())
        print ('Adding coinbase transaction')
        cbserial = Serializer.serialize(cbtrans)
        trans = pending_pool.get_trans()
        if not trans:
            return 
        trans.append(cbserial)
        bl = Block(0, '0', trans)
        bl.setup(trans)
        print ('All transactions are valid, block created') if (bl.validate()) else print ('Some of transactions are wrong, block declined')
        bc = Blockchain()
        bc.mine(bl) 
        print (bl.nonce)

    def do_gen(self, line):
        try:
            addr = open('miners_key', 'r').readline().replace('\n', '')
        except IOError:
            print ('No miners_key file!')
            return False
        privk = wallet.convert_from_wif(addr)
        publa = wallet.get_public_address(privk)
        cbtrans = CoinbaseTransaction(publa)
        cbtrans.signature, cbtrans.public_address = wallet.sign(privk, cbtrans.gethash())
        cbserial = Serializer.serialize(cbtrans)
        bl = Block(0, '0', [cbserial])
        bl.setup(cbserial)
        bl.validate()

if __name__ == '__main__':
    try:
        Shell().cmdloop()
    except KeyboardInterrupt:
        print(termcolors.RED + '\nClient interrupted' + termcolors.DEF)
      #  if os.path.isfile('mempool'):
      #      os.remove('mempool')
