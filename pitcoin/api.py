#!/usr/bin/env python

import flask, requests, struct, sys
from flask import json, jsonify, request, make_response
from tx_validator import *
from wallet import termcolors
from blockchain import Blockchain
from block import Block
from time import time
from syncdata import get_config, sync_node, clear_transactions, check_halving
from pending_pool import get_trans
from consensus import find_consensus
from pathlib import Path
from utxo_set import *
from operator import itemgetter
from transaction import CoinbaseTransaction
from serializer import Serializer, Deserializer, swap_bytes

home = str(Path.home()) + '/.pitcoin/'
my_url, PORT = get_config(False)

app = flask.Flask(__name__)
app.config["DEBUG"] = False

data = {}
data['blocks'] = []
data['ppool'] = []
data['nodes'] = []
data['utxo'] = []

blockchain = Blockchain()
sync_node(blockchain, data)
utxo_init(data)

if len(sys.argv) > 1 and sys.argv[1] == 'premine':
    print (termcolors.GRN + 'Premine mod on' + termcolors.DEF)
else:
    print (termcolors.YELL + 'Premine mod off' + termcolors.DEF)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

#home page, default route
@app.route('/', methods=['GET'])
def homepage():
    return '''<h1>Pitcoin web api</h1>
    <p>A prototype API for mastering bitcoin.</p>'''

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

#consensus command
@app.route('/consensus', methods=['GET'])
def get_consensus():
    link, leng = find_consensus(data)
    if leng == 0:
        return jsonify({'ok': 1})
    data['blocks'] = []
    print (link, leng)
    send_url = link + '/block/get'
    for i in range(leng):
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

@app.route('/block/get', methods=['GET'])
def get_block_by_index():
    print (request.args.get('height'))
    if not request.is_json:
        return jsonify({'error':'invalid object passed'}), 404
    index = request.get_json()['index']
    print (data['blocks'][index])
    return jsonify({'block': data['blocks'][index], 'success': True})

@app.route('/block', methods=['GET'])
def get_index_block():
    h = request.args.get('height')
    if not h:
        return jsonify({'error':'no height parameter passed'}), 404
    try:
        if (int(h) <= 0):
            raise ValueError
        if int(h) > len(data['blocks']):
            return jsonify({'error':'height exceeds blockchain length'}), 404
    except ValueError:
        return jsonify({'error':'height parameter must be a positive integer'}), 404
    return jsonify({'block height': h, 'block': data['blocks'][int(h) - 1], 'success': True})

@app.route('/block/last', methods=['GET'])
def get_last_block():
      return jsonify({'block': data['blocks'][len(data['blocks']) - 1], 'success': True})

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
    return jsonify({'valid': blockchain.is_valid_chain()}), 201

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

#adding a new block to blockchain
@app.route('/blocks/new', methods=['POST'])
def add_block_raw():
    if not request.is_json:
        return jsonify({'error':'invalid object passed'}), 404
    trans = get_trans(data)
    if (len(trans) == 0):
        print ('Empty mempool')
        return jsonify({'error':'Empty mempool'}), 404

    cbtrans = CoinbaseTransaction(request.get_json()['miner'], blockchain.reward)
    cbtrans.display_raw()
    cbtrans_serial = Serializer.serialize_raw(cbtrans, '', '').hex()
    cbtrans.tr_hash = swap_bytes(hashlib.sha256(hashlib.sha256(bytes.fromhex(cbtrans_serial)).digest()).hexdigest())
    utxo_add(data['utxo'], cbtrans)
    trans.append(cbtrans_serial)
    for i in trans:
        print (i)
    bl = Block(time(), 0, blockchain.last_hash, trans)
    bl.previous_hash = blockchain.last_hash
    blockchain.mine(bl)
    bl.heigth = len(data['blocks'])

#    return jsonify({'success': True}), 201
    jsblock = {}
    jsblock['hash'] = bl.hash
    jsblock['nonce'] = bl.nonce
    jsblock['previous_hash'] = bl.previous_hash
    jsblock['mroot'] = bl.mroot
    jsblock['transactions'] = bl.transactions
    jsblock['timestamp'] = bl.timestamp
    jsblock['heigth'] = bl.heigth

    if not bl.validate(blockchain.blocks[-3:], data['utxo']):
        print ('Invalid block')
        return jsonify({'error':'Invalid transaction in block'}), 404
    print ('Valid block')

    clear_transactions(data, bl.transactions)
    data['blocks'].append(jsblock)

    blockchain.blocks.append(bl)
    blockchain.last_hash = bl.hash
    with open(home + 'blockchain', 'w+') as f:
        json.dump(data['blocks'], f)

    check_halving(blockchain)
    return jsonify({'block': jsblock, 'success': True}), 201


def time_loop():
    return (1)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
