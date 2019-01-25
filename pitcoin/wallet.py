import sys, binascii, os, hashlib, base58
from ecdsa          import SigningKey, VerifyingKey, SECP256k1, BadSignatureError
#from ecpy.curves    import Curve, Point

#supportig functions and class
class termcolors:
    GRN = '\033[38;5;82m'
    RED = '\033[38;5;196m'
    YELL = '\033[38;5;11m'
    BLUE = '\033[38;5;27m'
    DEF = '\033[0m'

def print_help():
    forma = '{:' + str(len('broadcasttransactions')) + '}'
    print (termcolors.BLUE + '{}'.format('Pitcoin client usage: ') + termcolors.DEF)
    print (termcolors.GRN + forma.format('converttowif') + termcolors.DEF + ' - convert private key to WIF') 
    print (termcolors.GRN + forma.format('convertfromwif') + termcolors.DEF + ' - convert private key to WIF') 
    print (termcolors.GRN + forma.format('getnewprivatekey') + termcolors.DEF + ' - generate new private key') 
    print (termcolors.GRN + forma.format('getpulbickey') + termcolors.DEF + ' - generate public key from private key') 
    print (termcolors.GRN + forma.format('getpulbicaddress') + termcolors.DEF + ' - generate publicaddress from private key') 
    print (termcolors.GRN + forma.format('sign') + termcolors.DEF + ' - generate signature and public key for verification') 
    print (termcolors.GRN + forma.format('verify') + termcolors.DEF + ' - verify message usang public key and signature') 
    print (termcolors.GRN + forma.format('send') + termcolors.DEF + ' - form transaction with recepient\'s address and amount, sign it, validate and serialize')
    print (termcolors.GRN + forma.format('help') + termcolors.DEF + ' - display help message')
    print (termcolors.GRN + forma.format('exit') + termcolors.DEF + ' - close client')
    print ('-' * 80)
    print (termcolors.BLUE + 'In development' + termcolors.DEF)
    print (termcolors.YELL + forma.format('broadcasttransactions') + termcolors.DEF + ' - broadcast transactions in network')
    print (termcolors.YELL + forma.format('getbalance') + termcolors.DEF + ' - check balance of provided address')

#count checksum of the string
def checksum(s):
    sha1 = hashlib.sha256(binascii.unhexlify(s)).hexdigest().upper()
    sha2 = hashlib.sha256(binascii.unhexlify(sha1)).hexdigest().upper()
    return (sha2[0:8])

#convert private key from file to WIF format
def convert_to_wif(arg):
    s = '80' + str(arg) + '01'
    s += checksum(s)
    print (base58.b58encode(binascii.unhexlify(s)).decode())

#convert private key from file to WIF format
def convert_from_wif(arg):
    s = binascii.hexlify(base58.b58decode(arg)).decode()
    return (s[2:-10])

#generate new private key
def get_new_private_key():
    x = os.urandom(32)
    s = binascii.hexlify(x).decode().upper()
    return (s)

#getting public key from private, passed as argument
def get_public_key(arg):
    vk = SigningKey.from_string(binascii.unhexlify(arg), curve=SECP256k1).get_verifying_key();

    s = binascii.hexlify(vk.to_string()).decode('utf-8')
    x = s[:64]
    y = s[64:]
    s = ('03' if int(y[63], 16) & 1 else '02') + x
    return (s)
 
'''
    cv = Curve.get_curve('secp256k1')
    _Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
    _Gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
    P = Point(_Gx, _Gy, cv)
    Q = P * k
    s = hex(Q.x).replace('x', '2' if Q.y % 2 == 0 else '3').upper()

    sha = hashlib.sha256(binascii.unhexlify(s)).hexdigest().upper()
    print (Q.x)
    print (s, len(s))
    h = hashlib.new('ripemd160')
    h.update(binascii.unhexlify(sha))
    print (h.hexdigest())
'''
   
#get a public address in bitcoin form from private, passed as a parameter
def get_public_address(arg):
    s = get_public_key(arg)

    sha = hashlib.sha256(binascii.unhexlify(s)).hexdigest().upper()
    h = hashlib.new('ripemd160')
    h.update(binascii.unhexlify(sha))

    s = '00' +  h.hexdigest()
    sha1 = hashlib.sha256(binascii.unhexlify(s)).hexdigest().upper()
    sha2 = hashlib.sha256(binascii.unhexlify(sha1)).hexdigest().upper()
    s += sha2[0:8]
    s = s.upper()
    return (base58.b58encode(binascii.unhexlify(s)).decode())

#sign message with private key, returns signature and public key for verification
def sign(key, msg):
    sk = SigningKey.from_string(binascii.unhexlify(key), curve=SECP256k1)

    sig = sk.sign(bytes(msg, 'ascii'))
    print('Transaction signed')
    return (binascii.hexlify(sig).decode(), binascii.hexlify(sk.get_verifying_key().to_string()).decode())

#verify message with public key and signature
def verify(key, sig, msg):
    try:
        vk = VerifyingKey.from_string(binascii.unhexlify(key), curve=SECP256k1)
        vk.verify(binascii.unhexlify(sig), bytes(msg, 'ascii'))
        return (True)
    except BadSignatureError:
        return (False)

