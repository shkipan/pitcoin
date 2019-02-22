#!/usr/bin/env python

import flask, requests, struct, sys
from flask import json, jsonify, request, make_response, url_for, render_template
from tx_validator import *
from wallet import termcolors
from blockchain import Blockchain
from block import Block
from time import time, sleep, gmtime, strftime
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
    return render_template('home.html', title = 'Home page', data = data['blocks']), 201

#unspended outputs getter
@app.route('/utxo', methods=['GET'])
def return_utxo():
    adr = request.args.get('address')
    if not adr:
        return render_template('utxo.html', title = 'Utxo', data = data['utxo']), 201
    answer = utxo_get(data['utxo'], adr)
    if (len(answer) == 0):
        return jsonify({'error':'Invalid address'}), 404
    result = jsonify({'utxo_set': {
                'address': adr, 
                'tx': answer # if len(answer) > 0 else 'Empty'
                }})
    return render_template('utxo1.html', title = 'UTXO', data = {'address': adr, 'tx': answer}), 201

@app.route('/block', methods=['GET'])
def get_block():
    h = request.args.get('block_height')
    if not h:
        if not request.is_json:
            return jsonify({'error':'no height parameter passed'}), 202
        else:
            h = request.get_json()['index']
    try:
        if (int(h) <= 0):
            raise ValueError
        if int(h) > len(data['blocks']):
            return jsonify({'error':'height exceeds blockchain length'}), 202
    except ValueError:
        return jsonify({'error':'height parameter must be a positive integer'}), 202
    raw_txes = []
    for i in range(len(data['blocks'][int(h) - 1]["transactions"])):
        x = Deserializer.deserialize_raw(data['blocks'][int(h) - 1]["transactions"][i])
        jst = {}
        jst['version'] = x.version
        jst['inp'] = x.inputs
        jst['oup'] = x.outputs
        jst['locktime'] = x.timelock
        jst['tr_hash'] = x.tr_hash.hex()
        raw_txes.append(jst)
    ti = strftime("%a, %d %b %Y %H:%M:%S", gmtime(data['blocks'][int(h) - 1]['timestamp']))

    return render_template('block_index.html', title = 'Block', data = [data['blocks'][int(h) - 1], raw_txes, ti]), 201

#getter for blocks in blockchain
@app.route('/chain', methods=['GET'])
def get_chain():
    h = request.args.get('len')
    try:
        if (int(h) <= 0) or int(h) > len(data['blocks']):
            h = len(data['blocks'])
    except ValueError:
        h = len(data['blocks'])
    h = int(h)
    for bl in data['blocks'][-h:]:
        raw_txes_bl = []
        for i in range(len(bl["transactions"])):
            x = Deserializer.deserialize_raw(bl["transactions"][i])
            jst = {}
            jst['version'] = x.version
            jst['inp'] = x.inputs
            jst['oup'] = x.outputs
            jst['locktime'] = x.timelock

            jst['tr_hash'] = x.tr_hash.hex()
            raw_txes_bl.append(jst)
        bl['jsoni'] = raw_txes_bl
        bl['ti'] = strftime("%a, %d %b %Y %H:%M:%S", gmtime(bl['timestamp']))
    return render_template('blockchain.html', title = 'Blockchain', data = data['blocks'][-h:]), 201

#getter for length of blockchain
@app.route('/chain/length', methods=['GET'])
def get_chainlength():
    print (len(data['blocks']))
    return jsonify({'chainlength': len(data['blocks'])}), 201

#calculate balance of address
@app.route('/balance', methods=['GET'])
def get_balance():
    a = request.args.get('address')
    if not a:
        if (len(a) == 0):
            return jsonify({'error':'Empty field'}), 404
        if not request.is_json:
            return jsonify({'error':'invalid object passed'}), 404
        else:
            a = request.get_json()['addr']
    bal = utxo_balance(data['utxo'], a)
    return render_template('balance.html', title = 'Balance', data = [a, bal]), 201

#getter for transactions in mempool
@app.route('/transaction/', methods=['GET'])
def get_mempool():
    a = request.args.get('id')
    print (a)
    for bl in data['blocks']:
        for tr in bl['transactions']:
            x = Deserializer.deserialize_raw(tr)
            if (x.tr_hash.hex() == a):
                jst = {}
                jst['version'] = x.version
                jst['inp'] = x.inputs
                jst['oup'] = x.outputs
                for i in range(len(jst['oup'])):
                    jst['oup'][i]['spent'] = utxo_spent(data['utxo'], a, i)
                jst['locktime'] = x.timelock
                jst['tr_hash'] = x.tr_hash.hex()
                return render_template('transaction.html', title = 'Transaction', data = [bl, jst, a]), 201
    return jsonify({'error': 'Transaction ID is invalid'}), 404

#calculate balance of address
@app.route('/address', methods=['GET'])
def get_address_info():
    a = request.args.get('addr')
    if (len(a) == 0):
        return jsonify({'error':'Empty field'}), 404
    result = []
    for bl in data['blocks']:
        for tr in bl['transactions']:
            x = Deserializer.deserialize_raw(tr)
            for elem in x.outputs:
                if elem['address'] == a:
                    jst = {}
                    jst['timer'] = strftime("%a, %d %b %Y %H:%M:%S", gmtime(bl['timestamp']))


                    jst['version'] = x.version
                    jst['inp'] = []
                    for i in x.inputs:
                        s = utxo_get_trans_output(data['blocks'], i['tx_prev_hash'], i['tx_prev_index'])
                        jst['inp'].append(s if s else {'address': 'Coinbase'})

                    jst['oup'] = x.outputs
                    for i in range(len(jst['oup'])):
                        jst['oup'][i]['spent'] = utxo_spent(data['utxo'], x.tr_hash.hex(), i)
                    jst['locktime'] = x.timelock
                    jst['tr_hash'] = x.tr_hash.hex()
                    result.append(jst)
    if len(result) == 0:
        return jsonify({'error': 'Address is invalid'}), 404
    return render_template('address.html', title = 'Address Info', data = result), 201

#getter for blocks in blockchain
@app.route('/coinbase', methods=['GET'])
def get_reward():
    return jsonify({'reward': blockchain.reward}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4242, threaded=True)

