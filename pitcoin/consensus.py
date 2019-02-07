import flask
from flask import json, jsonify, request
from blockchain import Blockchain
from block import Block
import urllib.request

def find_consensus(data):
    bl_length = len(data['blocks'])
    node = ''
    for i in data['nodes']:
        try:
            print (i['node'])
            with urllib.request.urlopen('http://' + i['node'] + '/chain/length') as url:
                data = json.loads(url.read().decode())
                print (data)
                if (data['chainlength'] > bl_length):
                    node = 'http://' + i['node'] 
                    bl_length = data['chainlength']
        except urllib.error.URLError:
            print ('Error, can\'t connect to node:', i['node'])
    if (len(node) == 0):
        print ('No need to consensus')
        return '', 0
    else:
        print ('Consensus with node', node)
        return node, bl_length 

