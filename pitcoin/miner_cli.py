#!/usr/bin/env python
#wallet for creating transactions

import sys, cmd, os
import wallet, pending_pool
from wallet import termcolors
from block import Block
from time import time
from merkle import merkle_root
from blockchain import Blockchain
import json, requests, urllib.request
from transaction import CoinbaseTransaction
from serializer import Serializer

from syncdata import get_config
from pathlib import Path

#home = str(Path.home()) + '/.pitcoin/'
home = './.pitcoin/'

my_url, PORT = get_config()
print (my_url, PORT)
PORT = str(PORT)
send_url = my_url + ':' + PORT

class Shell(cmd.Cmd):
    prompt = termcolors.BLUE + 'miner-cli: ' + termcolors.DEF
    intro = "Pitcoin mining manager"

    def do_exit(self, line):
        print(termcolors.RED + 'Client stopped' + termcolors.DEF)
        sys.exit()

    def preloop(self):
        return None

    def emptyline(self):
        return None

    def do_EOF(self, line):
        return True

    def do_help(self, line):
        if len(line) == 0:
            wallet.print_mhelp()
        else:
            if line == 'add_node':
                print ('Syntax: add_node <address>')
                print ('Adds node URL to nodes list on server')
            elif line == 'mine':
                print ('Syntax: mine <complexity>')
                print ('Start mining process. Mined block will have <complexity> zeros at the beginning')
            elif line == 'consensus':
                print ('Syntax: consensus')
                print ('Connect to other nodes and get full chain, compare it and resolve conflicts by choosing more longer chain and replace current')
            elif line == 'help':
                print ('Syntax: help')
                print ('Displays help message.')
            elif line == 'exit':
                print ('Syntax: exit')
                print ('Stops wallet.')

    def default(self, line):
        print ('### Unknown command: ' + line)
        print ('-' * len('*** Unknown command: ' + line))
        wallet.print_mhelp()

    def do_add_node(self, line):
        try:
            if (len(line) == 0):
                raise ValueError
            print (line.split(' ')[0]) 
            x_url = send_url + '/nodes/add'
            data = {'node': line.split(' ')[0]}
            try:
                r = requests.post(url = x_url, json=data)
            except requests.exceptions.ConnectionError:
                print ('Unable to connect')
                return False
            d = json.loads(r.text)
            try:
                if (d['success']):
                    print ('node added to the list')
            except KeyError:
                print (d['error'] + ', node is not accepted')
        except ValueError:
            print ('Enter url address of the node')

    def do_getchainlength(self, line):
        with urllib.request.urlopen(send_url + '/chain/length') as url:
            data = json.loads(url.read().decode())
            print (data['chainlength'])

    def do_valid(self, line):
        with urllib.request.urlopen(send_url+ '/chain/valid') as url:
            data = json.loads(url.read().decode())
            print (data['valid'])

    def do_getchain(self, line):
        try:
            with urllib.request.urlopen(send_url+ '/chain') as url:
                data = json.loads(url.read().decode())
        except urllib.error.URLError:
            print ('Unable to connect')
            return False
        for i in data['blockchain']:
            print ('hash:', i['hash'])
            print ('nonce:', i['nonce'])
            print ('time:', i['timestamp'])
            print ('prev:', i['previous_hash'])
            print ('heigth', i['heigth'])
            print('_____________')

    def do_consensus(self, line):
        try:
            with urllib.request.urlopen(send_url+ '/consensus') as url:
                data = json.loads(url.read().decode())
        except urllib.error.URLError:
            print ('Unable to connect')
            return False

    def do_mine(self, line):
        try:
            addr = open('miners_key', 'r').readline().replace('\n', '')
        except IOError:
            print ('No miners_key file!')
            return False
        privk = wallet.convert_from_wif(addr)
        publa = wallet.get_public_address(privk)
        try:
            with urllib.request.urlopen(send_url+ '/coinbase') as url:
                data = json.loads(url.read().decode())
        except urllib.error.URLError:
            print ('Unable to connect')
            return
        rew = data['reward']
        cbtrans = CoinbaseTransaction(publa, rew)
        cbtrans.display_raw()
        cbtrans_serial = Serializer.serialize_raw(cbtrans, '', '').hex()
        data = {'miner': cbtrans_serial, 'address': publa}
        try:
            r  = requests.post(url = send_url+ '/blocks/new', json=data)
        except requests.exceptions.ConnectionError:
            print ('Unable to connect')
            return False
        d = json.loads(r.text)
        try:
            if (d['success']):
                print ('block accepted, hash:\n' + d['block']['hash'])
        except KeyError:
            print (d['error'] + ', block declined')
            return

    def do_start(self, line):
        try:
            r = requests.get(url = send_url + '/mine')
        except requests.exceptions.ConnectionError:
            print ('Unable to connect')
            return
        d = json.loads(r.text)
        print (d)



if __name__ == '__main__':
    try:
        Shell().cmdloop()
    except KeyboardInterrupt:
        print(termcolors.RED + '\nClient interrupted' + termcolors.DEF)
      #  if os.path.isfile('mempool'):
      #      os.remove('mempool')
