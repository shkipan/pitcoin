#!/usr/bin/env python
#wallet for creating transactions

import sys, os, cmd, base58, binascii
import wallet, tx_validator, pending_pool 
from transaction import Transaction
from tx_validator import verification
from serializer import Serializer, Deserializer
from wallet import termcolors
from block import Block

class Shell(cmd.Cmd):
    prompt = termcolors.BLUE + 'pitcoin-cli: ' + termcolors.DEF 
    intro = "Pitcoin wallet manager"

    private_key = None
    public_key = None
    serial = None

    def do_exit(self, line):
        print(termcolors.RED + 'Client stopped' + termcolors.DEF)
   #     if os.path.isfile('mempool'):
   #         os.remove('mempool')
        sys.exit()

    def preloop(self):
        if os.path.isfile('mempool'):
            os.remove('mempool')
        f = open('mempool', 'a')
        f.close

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

    def do_new(self, line):
        privk = wallet.get_new_private_key()
        publk = wallet.get_public_key(privk)
        publaddr = wallet.get_public_address(privk)
        print ('private key:     ', privk)
        print ('public address:  ', publaddr)
        open('address', 'w+').write(publaddr)
        self.private_key = privk
        self.public_key = publk

    def do_import(self, line):
        path = line.split(' ')[0]
        try:
            wif = open(path, 'r').readline().replace('\n', '')
            self.private_key = wallet.convert_from_wif(wif)
            publk = wallet.get_public_key(self.private_key)
            publaddr = wallet.get_public_address(self.private_key)
            open('address', 'w+').write(publaddr)
            self.public_key = publk
            print ('private key:     ', self.private_key)
            print ('public address:  ', publaddr)
        except IOError:
            print ('Can\'t open file ' + path)

    def do_converttowif(self, line):
        if (self.private_key):
            wallet.convert_to_wif(self.private_key)
        else:
            print ('No private key generated!')

    def do_getpublickey(self, line):
        if (self.private_key):
            s = wallet.get_public_key(self.private_key)
            print (s)
            self.public_key = s
        else:
            print ('No private key generated!')

    def do_getpublicaddress(self, line):
        if (self.private_key):
            s = wallet.get_public_address(self.private_key)
            print (s)
        else:
            print ('No private key generated!')

    def do_convertfromwif(self, line):
        if (len(line) > 0):
            s = wallet.convert_from_wif(line.split(' ')[0])
            print (s)
        else:
            print ('Enter key in WIF as an argument!')

    def do_send(self, line):
        if (len(line.split(' ')) < 2):
            print ('Enter recipient\'s address and amount')
        else:
            if (self.private_key):
                try:
                    publk = open('address', 'r').readline().replace('\n', '')
                    if int(line.split(' ')[1]) > 65535 or int(line.split(' ')[1]) < 1:
                       raise ValueError()
                    x = Transaction(publk, line.split(' ')[0], int(line.split(' ')[1]))
                    x.signature, x.public_address = wallet.sign(self.private_key, x.gethash())
                    if (verification(x)):
                        print (termcolors.GRN + 'Transaction verified' + termcolors.DEF)
                        self.serial = Serializer.serialize(x)
                    else:
                        print (termcolors.RED + 'Transaction declined' + termcolors.DEF)
                except IOError:
                    print ('Can\'t open address file')
                except ValueError:
                    print (termcolors.RED + 'Error! ' + termcolors.DEF + 'Coins\' number must be integer from 1 to 65535 coins')
            else:
                print ('No private key generated!')

    def do_broadcast(self, line):
        if not self.serial:
            return 
        pending_pool.add_trans(self.serial)
        print ('Transaction added to mempool')

    def do_balance(self, line):
        print ('Here will be shown your balance')

    def do_printmempool(self, line):
        pending_pool.get_trans()

if __name__ == '__main__':
    try:
        Shell().cmdloop()
    except KeyboardInterrupt:
        print(termcolors.RED + '\nClient interrupted' + termcolors.DEF)
   #     if os.path.isfile('mempool'):
    #        os.remove('mempool')
        if Shell().private_key:
            Shell().private_key = None

