import sys, binascii, os, hashlib, base58, ecdsa, requests, json
from ecdsa          import SigningKey, VerifyingKey, SECP256k1, BadSignatureError
from operator import itemgetter

#supporting functions and class
class termcolors:
    GRN = '\033[38;5;82m'
    RED = '\033[38;5;196m'
    YELL = '\033[38;5;11m'
    BLUE = '\033[38;5;27m'
    DEF = '\033[0m'

def print_help():
    forma = '{:' + str(len('broadcasttransactions')) + '}'
    print (termcolors.BLUE + '{}'.format('Pitcoin wallet\'s client usage: ') + termcolors.DEF)
    print (termcolors.GRN + forma.format('balance') + termcolors.DEF + ' - check balance of provided address')
    print (termcolors.GRN + forma.format('broadcast') + termcolors.DEF + ' - broadcast last serialized transaction in network')
    print (termcolors.GRN + forma.format('import') + termcolors.DEF + ' - generate new private key and public address') 
    print (termcolors.GRN + forma.format('new') + termcolors.DEF + ' - generate new private key and public address') 
    print (termcolors.GRN + forma.format('send') + termcolors.DEF + ' - form transaction, sign it, validate and serialize')
    print (termcolors.GRN + forma.format('help') + termcolors.DEF + ' - display help message')
    print (termcolors.GRN + forma.format('exit') + termcolors.DEF + ' - close client')
    print ('-' * 80)
    print ('For detailed info type \'help <command>\'')
#    print (termcolors.BLUE + 'In development' + termcolors.DEF)

def print_mhelp():
    forma = '{:' + str(len('broadcasttransactions')) + '}'
    print (termcolors.BLUE + '{}'.format('Pitcoin miner\'s client usage: ') + termcolors.DEF)
    print (termcolors.GRN + forma.format('add_node') + termcolors.DEF + ' - add node url to node\'s list') 
    print (termcolors.GRN + forma.format('consensus') + termcolors.DEF + ' - connect to other nodes, resolve conflicts by getting the longest chain')
    print (termcolors.GRN + forma.format('mine') + termcolors.DEF + ' - start mining process with passed complexity') 
    print (termcolors.GRN + forma.format('help') + termcolors.DEF + ' - display help message')
    print (termcolors.GRN + forma.format('exit') + termcolors.DEF + ' - close client')
    print ('-' * 80)
#    print (termcolors.BLUE + 'In development' + termcolors.DEF)
    print ('For detailed info type \'help <command>\'')


#count checksum of the string
def checksum(s):
    try:
        sha1 = hashlib.sha256(binascii.unhexlify(s)).hexdigest()
        sha2 = hashlib.sha256(binascii.unhexlify(sha1)).hexdigest()
        return (sha2[0:8])
    except binascii.Error:
        print ('Invalid string length!')
        sys.exit(1)

#convert private key from file to WIF format
def convert_to_wif(arg):
    s = 'ef' + str(arg) + '01'
    s += checksum(s)
    try:
        s = base58.b58encode(binascii.unhexlify(s)).decode()
    except binascii.Error:
        print ('Invalid string length!')
        sys.exit(1)
    return s

def get_wif_from_file():
    try:
        f = open('privkey', 'r')
    except IOError:
        print ('No prikey file')
        return
    s = f.readline().replace('\n', '')
    convert_to_wif(s)
    print (s)

#convert private key from file to WIF format
def convert_from_wif(arg):
    try:
        s = binascii.hexlify(base58.b58decode(arg)).decode()
    except binascii.Error:
        print ('Invalid string length!')
        sys.exit(1)

    return (s[2:-10])

#generate new private key
def get_new_private_key():
    x = os.urandom(32)
    s = binascii.hexlify(x).decode()
    return (s)

#getting public key from private, passed as argument
def get_public_key(arg, compressed=True):
    vk = SigningKey.from_string(binascii.unhexlify(arg), curve=SECP256k1).get_verifying_key();

    try:
        s = binascii.hexlify(vk.to_string()).decode('utf-8')
    except binascii.Error:
        print ('Invalid string length!')
        sys.exit(1)
    if not compressed:
        return ('04' + s)

    x = s[:64]
    y = s[64:]
    s = ('03' if int(y[63], 16) & 1 else '02') + x
    return (s)
   
#get a public address in bitcoin form from private, passed as a parameter
def get_public_address(arg):
    s = get_public_key(arg)
    try:
        sha = hashlib.sha256(binascii.unhexlify(s)).hexdigest()
        h = hashlib.new('ripemd160')
        h.update(binascii.unhexlify(sha))
 
        s = '6f' +  h.hexdigest()
        s += checksum(s)
        s = s.upper()
        s = base58.b58encode(binascii.unhexlify(s)).decode()
    except binascii.Error:
        print ('Invalid string length!')
        sys.exit(1)
    return (s)

#sign message with private key, returns signature and public key for verification
def sign(key, msg):
    try:
        sk = SigningKey.from_string(binascii.unhexlify(key), curve=SECP256k1)
        sig = sk.sign(bytes.fromhex(msg), sigencode=ecdsa.util.sigencode_der)
        print('Transaction signed')
        sig = binascii.hexlify(sig).decode()
        publk = binascii.hexlify(sk.get_verifying_key().to_string()).decode()
    except binascii.Error:
        print ('Invalid string length!')
        sys.exit(1)
    return sig, publk
  
#verify message with public key and signature
def verify(key, sig, msg):
    try:
        vk = VerifyingKey.from_string(binascii.unhexlify(key), curve=SECP256k1)
        vk.verify(binascii.unhexlify(sig), bytes.fromhex(msg), sigdecode=ecdsa.util.sigdecode_der)
        return (True)
    except BadSignatureError:
        return (False)

def get_inputs(pa, send_url):
    try:
        r = requests.get(url=send_url)
    except requests.exceptions.ConnectionError:
        print ('Unable to connect')
        return []
    d = json.loads(r.text)
    try:
        if len(d) == 0:
            print ('No unspent output!')
            return []
    except KeyError:
        return
    return sorted(d['utxo_set']['tx'], key=itemgetter('amount'))

def get_testnet_inputs(sender):
    send_url = 'https://testnet.blockchain.info/unspent?active=' + sender
    try:
        r = requests.get(url=send_url)
    except requests.exceptions.ConnectionError:
        print ('Unable to connect')
        return []
    try:
        d = json.loads(r.text)
    except json.decoder.JSONDecodeError:
        return []
    res = []
    for item in d['unspent_outputs']:
        tx ={
                'amount': item['value'],
                'tx_prev_index': item['tx_output_n'],
                'tx_prev_hash': item['tx_hash_big_endian'],
                'script': item['script']
                } 
        res.append(tx)
    return sorted(res, key=itemgetter('amount'))

if __name__ == '__main__':
    get_testnet_inputs('mv13YQAqcat77LVNVU2b8qh3GHiqCik6fi')


