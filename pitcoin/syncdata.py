import flask
from flask import json, jsonify
import socket
from pathlib import Path

home = str(Path.home()) + '/.pitcoin/'

def validate_url(st):
    try:
        socket.inet_aton(st)
        return True
    except:
        return False

def get_config(muted = True):
    conf = {
            'url':'0.0.0.0',
            'port':5000
    }
    try:
        with open(home + 'config', 'r') as f:
            if not muted:
                print ('Config file opened')
            tex = f.read().replace(' ', '').split('\n')
            for string in tex:
                if len(string) == 0 or len(string.split('=')) != 2:
                    continue
                for i in conf:
                    if string.split('=')[0] == i:
                        conf[i] = string.split('=')[1]
                        if i == 'url':
                            if not validate_url(string.split('=')[1]):
                                conf['url'] = '0.0.0.0'

    except:
        if not muted:
            print ('No config file!')
    return 'http://' + conf['url'], conf['port']

def sync_node(blockchain, data):
    for i in blockchain.blocks:
        t = {
            'timestamp': i.timestamp,
            'nonce':i.nonce,
            'mroot':i.mroot,
            'transactions':i.transactions,
            'hash':i.hash,
            'previous_hash':i.previous_hash,
            'heigth': i.heigth
        }
        data['blocks'].append(t)
    with open(home + 'blockchain', 'w+') as f:
        json.dump(data['blocks'], f)

    try:
        with open(home + 'mempool', 'r') as f:
            print ('Mempool file opened')
            tex = f.read()
            fpool = json.loads(tex)
            for item in fpool:
                data['ppool'].append(item)
    except:
        print ('No mempool file!')
    try:
        with open(home + 'nodes', 'r') as f:
            print ('Nodes file opened')
            tex = f.read()
            fnodes = json.loads(tex)
            for item in fnodes:
                data['nodes'].append(item)
    except:
        print ('No nodes file!')
     
def clear_transactions(data, arr):
    x = []
    for trans in arr:
        for item in data['ppool']:
            if item['serial'] == trans:
                x.append(item)
    x1 = (i for i in data['ppool'] if i not in x)
    data['ppool'] = []
    for i in x1:
        data['ppool'].append(i)
    with open(home + 'mempool', 'w+') as f:
        json.dump(data['ppool'], f)

def check_halving(blockchain):
    le = len(blockchain.blocks)
    if le % 5 == 0:
        blockchain.reward = int(blockchain.reward / 2)
    return (1)
