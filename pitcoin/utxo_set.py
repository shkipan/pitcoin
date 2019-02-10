import sys, hashlib, base58
import json, requests, urllib.request
from serializer import Deserializer
from operator import itemgetter

from syncdata import get_config
from pathlib import Path

home = str(Path.home()) + '/.pitcoin/'
my_url, PORT = get_config()
PORT = str(PORT)

def utxo_get(utxo, address):
    for elem in utxo:
        if len(elem['outputs']) == 0:
            utxo.remove(elem)
    result = []
    for trans in utxo:
        for i in trans['outputs']:
            if i['address'] == address:
                result.append({
                    'tx_prev_hash': trans['tx_id'], 
                    'tx_prev_index': i['index'], 
                    'amount': i['amount'],
                    'script': i['script']
                })
    return (result)

def utxo_balance(utxo, address):
    for elem in utxo:
        if len(elem['outputs']) == 0:
            utxo.remove(elem)
    inputs = utxo_get(utxo, address)
    bal = 0
    for i in inputs:
        bal += i['amount']

    return (bal)

def utxo_select_inputs(out_set, fee, amount):
    res = []
    bal = 0
    for i in out_set:
        bal += i['amount']
        if (i['amount'] > amount + fee):
            res.append(i)
            return (res)
    if (bal < amount + fee):
        return res
    outs = sorted(out_set, key=itemgetter('amount'), reverse=True)
    i = 0
    bal = 0
    while bal < amount + fee:
        bal += outs[i]['amount']
        res.append(outs[i])
        i += 1
    return res

def utxo_create_outputs(sender, recipient, amount, fee, inputs):
    bal = 0
    out = []
    for item in inputs:
        bal += item['amount']
    diff = bal - amount - fee
    out.append({'value': amount, 'address': recipient})
    out.append({'value': diff, 'address': sender})
    return out

def utxo_add(utxo, trans):
    for elem in utxo:
        if len(elem['outputs']) == 0:
            utxo.remove(elem)
    for i in range(trans.inputs_num):
        item = trans.inputs[i]
        for tr in utxo:
            if tr['tx_id'] == item['tx_prev_hash']:
                for index in range(len(tr['outputs'])):
                    if tr['outputs'][index]['index'] == item['tx_prev_index']:
                        tr['outputs'].pop(index)
                        break
    for elem in utxo:
        if len(elem['outputs']) == 0:
            utxo.remove(elem)
    for i in range(trans.outputs_num):
        hashed_pubk = base58.b58decode_check(trans.outputs[i]['address'])[1:].hex()
        script = '76a914' + hashed_pubk + '88ac'
        utxo.append({
            'tx_id': trans.tr_hash.hex(),
            'outputs':[
                {
                    'address': trans.outputs[i]['address'],
                    'index': i,
                    'script': script,
                    'amount': trans.outputs[i]['value']},
        ]})

def utxo_get_script(utxo, trans_hash, tx_prev_index):
    for item in utxo:
        if trans_hash == item['tx_id']:
            for index in range(len(item['outputs'])):
                if item['outputs'][index]['index'] == tx_prev_index:
                    return item['outputs'][index]['script']

#TO DEL_______________________________________________________

def utxo_init(data):
    data['utxo'] = []
    blocks = data['blocks']
    for block in blocks:
        print (block['hash'])
        for trans in block['transactions']:
            x = Deserializer.deserialize_raw(trans)
            utxo_add(data['utxo'], x)
            x.display_raw()
    '''
    data['utxo'].append(
            {   'tx_id': 'b8c80067725f5d2ef41bba57096dbe0f46a26aa6e4ad409d2500a3cc226e3e91',
                'outputs':  [
                    {
                        'address': 'mkADfzin6WwT7tLVWgpj7DcgiJ3nBp4HDh',
                        'index': 0,
                        'script': '76a91432ecbb1b78a870466ed165d98165fba6ddb3828488ac',
                        'amount': 5},
                    {
                        'address': 'n2Zp9LVCnQF5Wvpw8G9ogKb4DGDR9PmXvR',
                        'index': 1,
                        'script': '76a9149ee1c9c57e86f8d1264a02f8af8a5c2543f787bc88ac',
                        'amount': 50},
                   {
                        'address': 'mtKx9fXxQuuAdr21jmFg9ZbRrSk8GLYsaG',
                        'index': 2,
                        'script': '76a9149ee1c9c57e86f8d1264a02f8af8a5c2543f787bc88ac',
                        'amount': 50},
                ]})
    data['utxo'].append(
            {   'tx_id': '13e4d29d2fe5f500d5376ff3bd2bdafc34fd74b3164811d061dd229c7f520b46',
                'outputs':  [
                    {
                        'address': 'mtKx9fXxQuuAdr21jmFg9ZbRrSk8GLYsaG',
                        'index': 0,
                        'script': '76a9149ee1c9c57e86f8d1264a02f8af8a5c2543f787bc88ac',
                        'amount': 11},
                    {
                        'address': 'mkADfzin6WwT7tLVWgpj7DcgiJ3nBp4HDh',
                        'index': 1,
                        'script': '76a91432ecbb1b78a870466ed165d98165fba6ddb3828488ac',
                        'amount': 42},
                   {
                        'address': 'n2Zp9LVCnQF5Wvpw8G9ogKb4DGDR9PmXvR',
                        'index': 2,
                        'script': '76a9149ee1c9c57e86f8d1264a02f8af8a5c2543f787bc88ac',
                        'amount': 25},
                ]})
    data['utxo'].append(
            {   'tx_id': '6991f08090f31511d185e8dcae6e3a287d08aa148ffd713d6f16a89dfd4745ae',
                'outputs':  [
                    {
                        'address': 'mkADfzin6WwT7tLVWgpj7DcgiJ3nBp4HDh',
                        'index': 0,
                        'script': '76a91432ecbb1b78a870466ed165d98165fba6ddb3828488ac',
                        'amount': 10000000000000}
                       ]})
                       '''

  
#TO DEL_______________________________________________________

def get_fees(trans):
    fees = 0
    for i in trans:
        x = Deserializer.deserialize_raw(i)
        x.display_raw()
    return fees

if __name__ == '__main__':
    x = [
        "0100000001ae4547fd9da8166f3d71fd8f14aa087d283a6eaedce885d11115f39080f09169000000006b4830450221008191af68e0a1b397ad6dc811c7388f40a5cdf6005c49642767c0a22bb5077ef70220482c573ce44b8ffb1ccdbcaedb5f6b29035e90a5dce986feeabe295424e596b70121030bd6af4572a569e8c512f686cd5b9f414a58b71cf1a54543b20afdbe9129b969ffffffff022a000000000000001976a9149ee1c9c57e86f8d1264a02f8af8a5c2543f787bc88ac35000000000000001976a9149ee1c9c57e86f8d1264a02f8af8a5c2543f787bc88ac00000000", 
        "0100000001eecd4daf4b5ba3a1bb251618509b1e833f51b90ece3790a2e5e882ab81d3f0fd010000006b483045022100af787dd98b3765b18a49d2eff10840b3b9440a512d4b78ef156c9f636981088e022066f2536a7ab7aff026063806e2ab692126cdcb601db0dcb458d755db2bfb41810121030bd6af4572a569e8c512f686cd5b9f414a58b71cf1a54543b20afdbe9129b969ffffffff022a000000000000001976a9149ee1c9c57e86f8d1264a02f8af8a5c2543f787bc88ac06000000000000001976a9149ee1c9c57e86f8d1264a02f8af8a5c2543f787bc88ac00000000", 
        "01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff406cb5ec8df8634e7c890494fc764c6bdcc3596271f98cc9bc2a34971a06e6361ebd2587d69dff801ddb24335bf051138a8cb64bc7256b8ce7797b4e7e6dab8bd3ffffffff0132000000000000001976a914e3dd7e774a1272aeddb18efdc4baf6e14990edaa88ac00000000"
      ]
    print (get_fees(x))
