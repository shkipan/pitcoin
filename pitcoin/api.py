#!/usr/bin/env python

import flask, requests, struct, sys
from flask import json, jsonify, request, make_response, url_for, render_template
from tx_validator import *
from wallet import termcolors
from blockchain import Blockchain
from block import Block
from time import time, sleep
from syncdata import *
from pending_pool import get_trans
from consensus import find_consensus
from pathlib import Path
from utxo_set import *
from operator import itemgetter
from transaction import CoinbaseTransaction
from serializer import Serializer, Deserializer, swap_bytes
import threading

#home = str(Path.home()) + '/.pitcoin/'
home = './.pitcoin/'
my_url, PORT = get_config(False)

app = flask.Flask(__name__)
app.config["DEBUG"] = True

data = {}
data['blocks'] = []
data['ppool'] = []
data['nodes'] = []
data['utxo'] = []
data['mining'] = False
data['mining_thread'] = None

premine = False
if len(sys.argv) > 1 and sys.argv[1] == '-premine':
    print (termcolors.GRN + 'Premine mod on' + termcolors.DEF)
    premine = True
else:
    print (termcolors.YELL + 'Premine mod off' + termcolors.DEF)
blockchain = Blockchain(premine)
blockchain.is_valid_chain(data['utxo'])

sync_node(blockchain, data)
utxo_init(data)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

#home page, default route
@app.route('/', methods=['GET'])
def homepage():
    return 'Hello world!', 201

#unspended outputs getter
@app.route('/utxo', methods=['GET'])
def return_utxo():
    adr = request.args.get('address')
    if not adr:
        return jsonify({'utxo_set': data['utxo']}), 201
    answer = utxo_get(data['utxo'], adr)
    result = jsonify({'utxo_set': {
                'address': adr, 
                'tx': answer # if len(answer) > 0 else 'Empty'
                }})

    return result, 201

#supply getter
@app.route('/supply', methods=['GET'])
def return_suply():
    return jsonify({'supply': utxo_supply(data['utxo']), 'success': True})

#consensus command
@app.route('/consensus', methods=['GET'])
def get_consensus():
    link, leng = find_consensus(data)
    if leng == 0:
        return jsonify({'ok': 1})
    data['blocks'] = []
    print (link, leng)
    send_url = link + '/block'
    for i in range(1, leng + 1):
        send_data = {'index': i}
        r = requests.get(url=send_url, json = send_data)
        d = json.loads(r.text)
        try:
            if (d['success']):
                data['blocks'].append(d['block'])
        except KeyError:
            print (d['error'])
    with open(home + 'blockchain', 'w+') as f:
        json.dump(data['blocks'], f)
    utxo_init(data)
    return jsonify({'blockchain': 1})

@app.route('/block', methods=['GET'])
def get_block():
    h = request.args.get('block_height')
    if not h:
        if not request.is_json:
            return jsonify({'error':'no height parameter passed'}), 404
        else:
            h = request.get_json()['index']
    try:
        if (int(h) <= 0):
            raise ValueError
        if int(h) > len(data['blocks']):
            return jsonify({'error':'height exceeds blockchain length'}), 404
    except ValueError:
        return jsonify({'error':'height parameter must be a positive integer'}), 404
    return jsonify({'block height': h, 'block': data['blocks'][int(h) - 1], 'success': True}), 201

@app.route('/block/last', methods=['GET'])
def get_last_block():
      return jsonify({'block': data['blocks'][len(data['blocks']) - 1], 'success': True}), 201

#adding a new block to blockchain
@app.route('/block/receive', methods=['POST'])
def receive_block():
    if not request.is_json:
        return jsonify({'error':'invalid object passed'}), 404
    bl = request.get_json()
    print ('block received!')
    print (bl)
    if data['mining_thread']:
        data['mining_thread'].do_run = False
        data['mining_thread'].join()
    return (jsonify({'success': True})), 201

#adding a new block to blockchain
@app.route('/blocks/new', methods=['POST'])
def add_block_raw():
    if not request.is_json:
        return jsonify({'error':'invalid object passed'}), 404
    cbtrans_serial = request.get_json()['miner']
    cbtrans = Deserializer.deserialize_raw(cbtrans_serial)
    cbtrans.tr_hash = swap_bytes(hashlib.sha256(hashlib.sha256(bytes.fromhex(cbtrans_serial)).digest()).hexdigest())
    trans = [cbtrans_serial]
    if (len(get_trans(data)) > 0):
        trans.append(get_trans(data))
    bl = Block(time(), 0, blockchain.last_hash, trans)
    bl.target = blockchain.target
    blockchain.mine(bl)
    bl.heigth = len(data['blocks'])
    if not bl.validate(blockchain.blocks[-3:], data['utxo']):
        print ('Invalid block')
        return jsonify({'error':'Invalid transaction in block'}), 404
    print ('Valid block')
    utxo_add(data['utxo'], cbtrans)
    clear_transactions(data, bl.transactions)
    jsblock = create_js_block(bl)
    data['blocks'].append(jsblock)
    blockchain.blocks.append(bl)
    blockchain.last_hash = bl.hash
    with open(home + 'blockchain', 'w+') as f:
        json.dump(data['blocks'], f)

    check_halving(blockchain)
    return jsonify({'block': jsblock, 'success': True}), 201

#getter for blocks in blockchain
@app.route('/chain', methods=['GET'])
def get_chain():
    return jsonify({'blockchain': data['blocks']})

#getter for length of blockchain
@app.route('/chain/length', methods=['GET'])
def get_chainlength():
    print (len(data['blocks']))
    return jsonify({'chainlength': len(data['blocks'])}), 201

#checking validity of all blocks in blockchain
@app.route('/chain/valid', methods=['GET'])
def get_validity():
    return jsonify({'valid': blockchain.is_valid_chain(utxo)}), 201

#calculate balance of address
@app.route('/balance', methods=['GET'])
def get_balance():
    a = request.args.get('address')
    if not a:
        if not request.is_json:
            return jsonify({'error':'invalid object passed'}), 404
        else:
            a = request.get_json()['addr']
    bal = utxo_balance(data['utxo'], a)
    return jsonify({'address': a, 'utxo_balance': bal, 'success': True}), 201

#getter for available nodes
@app.route('/nodes', methods=['GET'])
def get_nodes():
    return jsonify({'nodes': data['nodes']}), 201

#adding a new node
@app.route('/nodes/add', methods=['POST'])
def add_node():
    if not request.is_json:
        return jsonify({'error':'invalid object passed'}), 404
    new_node = request.get_json()['node']
    for i in data['nodes']:
        if new_node == i['node']:
            return jsonify({'nodes': data['nodes'], 'success': True}), 201
    data['nodes'].append({'node': new_node})
    with open(home + 'nodes', 'w+') as f:
        json.dump(data['nodes'], f)
    return jsonify({'nodes': data['nodes'], 'success': True}), 201

#getter for transactions in mempool
@app.route('/transaction/pendings', methods=['GET'])
def get_mempool():
    if (len(data['ppool']) == 0):
        return jsonify({'mempool': 'empty'}), 201

    return jsonify({'mempool': data['ppool']}), 201

#adding a new transaction to mempool
@app.route('/transactions/new', methods=['POST'])
def add_raw_transaction():
    if not request.is_json:
        return jsonify({'error':'invalid object passed'}), 404
    trans = {
        'serial': request.get_json()['serial'],
        'id': 0 if len(data['ppool']) == 0 else data['ppool'][-1]['id'] + 1
    }
    try:
        x = Deserializer.deserialize_raw(trans['serial'])
    except struct.error:
        print ('Invalid transaction format')
        return jsonify({'error':'Invalid transaction format'}), 404
     
    x.display_raw()
    val = validate_raw(data['utxo'], x)
    if (val == False):
        print ('Transaction was not validated')
        return jsonify({'error':'Transaction is invalid'}), 404
    utxo_add(data['utxo'], x)
    data['ppool'].append(trans)
    with open(home + 'mempool', 'w+') as f:
        json.dump(data['ppool'], f)
    return jsonify({'success': True}), 201

#getter for blocks in blockchain
@app.route('/coinbase', methods=['GET'])
def get_reward():
    return jsonify({'reward': blockchain.reward})

data['mining_result'] = []

def print_sth(cbtrans_serial, arr):
    t = threading.currentThread()
    while (getattr(t, 'do_run', True)):
        n = 0
        cbtrans = Deserializer.deserialize_raw(cbtrans_serial)
        cbtrans.tr_hash = swap_bytes(hashlib.sha256(hashlib.sha256(bytes.fromhex(cbtrans_serial)).digest()).hexdigest())
        trans = []
        trans.append(cbtrans_serial)
        if (len(get_trans(data)) > 0):
            trans.append(get_trans(data))
        bl = Block(time(), 0, blockchain.last_hash, trans)
        bl.heigth = len(arr)
        bl.target = blockchain.target
#        print (blockchain.target)
        while getattr(t, 'do_run', True) and n < 2 ** 32:
            bl.nonce = n
            bl.calculate_hash()
#            print (n, bl.hash)
            if int(bl.hash, 16) < blockchain.target:
                break
            n += 1
        if not getattr(t, 'do_run', True):
            return
        print (bl.timestamp - arr[len(arr) - 1].timestamp)
        if bl.timestamp - arr[len(arr) - 1].timestamp < 5:
            blockchain.target = int(0.75 * blockchain.target)
        else:
            blockchain.target = int(1.25 * blockchain.target)
        arr.append(bl)
        jsblock = create_js_block(bl)
        data['blocks'].append(jsblock)
        send_new_block(data['nodes'], jsblock)

@app.route('/mine', methods=['POST'])
def mining():
    print ('MINING BITCH')
    if not request.is_json:
        return jsonify({'error':'invalid object passed'}), 404
    data['mining'] = not data['mining']
    if data['mining']:
        cbtrans_serial = request.get_json()['miner']
        print ('mining started')
        data['mining_thread'] = threading.Thread(target=print_sth, args = (cbtrans_serial, blockchain.blocks, ))
        data['mining_thread'].start()
        data['mining_thread'].join()
    else:
        print ('mining ended')
        data['mining_thread'].do_run = False
        data['mining_thread'].join()
        with open(home + 'blockchain', 'w+') as f:
            json.dump(data['blocks'], f)
        ts = 0
        for i in range(1, len(blockchain.blocks) + 1):
            ts += (blockchain.blocks[i].timestamp - blockchain.blocks[i - 1].timestamp)
            print (i, blockchain.blocks[i].timestamp, ts)
            print ('average time of mining', ts / i)
            
        print ('average', ts / (len(blockchain.blocks) - 1))

        data['mining'] = False
    return jsonify({'success': True}), 201

def create_js_block(bl):
    jsblock = {}
    jsblock['hash'] = bl.hash
    jsblock['nonce'] = bl.nonce
    jsblock['previous_block_hash'] = bl.previous_hash
    jsblock['merkle_root'] = bl.mroot
    jsblock['transactions'] = bl.transactions
    jsblock['timestamp'] = bl.timestamp
    jsblock['heigth'] = bl.heigth
    jsblock['target'] = bl.target
    jsblock['version'] = bl.version
    return (jsblock)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, threaded=True)

