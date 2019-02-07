import sys, hashlib, base58
import json, requests, urllib.request
from operator import itemgetter

from syncdata import get_config
from pathlib import Path

home = str(Path.home()) + '/.pitcoin/'
my_url, PORT = get_config()
PORT = str(PORT)

def utxo_get(utxo, address):
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


#TO DEL_______________________________________________________

def utxo_init(data):
    data['utxo'].append(
            {   'tx_id': 'b8c80067725f5d2ef41bba57096dbe0f46a26aa6e4ad409d2500a3cc226e3e91',
                'outputs':  [
                    {
                        'address': 'mv13YQAqcat77LVNVU2b8qh3GHiqCik6fi',
                        'index': 0,
                        'script': '76a9149ee1c9c57e86f8d1264a02f8af8a5c2543f787bc88ac',
                        'amount': 50},
                    {
                        'address': 'n2Zp9LVCnQF5Wvpw8G9ogKb4DGDR9PmXvR',
                        'index': 0,
                        'script': '76a9149ee1c9c57e86f8d1264a02f8af8a5c2543f787bc88ac',
                        'amount': 50},
                   {
                        'address': 'mtKx9fXxQuuAdr21jmFg9ZbRrSk8GLYsaG',
                        'index': 0,
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
                        'address': 'mv13YQAqcat77LVNVU2b8qh3GHiqCik6fi',
                        'index': 0,
                        'script': '76a9149ee1c9c57e86f8d1264a02f8af8a5c2543f787bc88ac',
                        'amount': 42},
                   {
                        'address': 'n2Zp9LVCnQF5Wvpw8G9ogKb4DGDR9PmXvR',
                        'index': 0,
                        'script': '76a9149ee1c9c57e86f8d1264a02f8af8a5c2543f787bc88ac',
                        'amount': 25},
                ]})
    data['utxo'].append(
            {   'tx_id': '6991f08090f31511d185e8dcae6e3a287d08aa148ffd713d6f16a89dfd4745ae',
                'outputs':  [
                    {
                        'address': 'mv13YQAqcat77LVNVU2b8qh3GHiqCik6fi',
                        'index': 0,
                        'script': '76a9149ee1c9c57e86f8d1264a02f8af8a5c2543f787bc88ac',
                        'amount': 1}
                       ]})

  
#TO DEL_______________________________________________________

