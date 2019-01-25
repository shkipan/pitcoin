import binascii, base58, hashlib
from transaction import Transaction
from wallet import checksum, verify

def check_aval(trans):
    try:
        ssend = '0' * 34 if (trans.sender == '0' * 34) else binascii.hexlify(base58.b58decode(trans.sender)).decode()
        srec = binascii.hexlify(base58.b58decode(trans.recipient)).decode()
        if ssend != '0' * 34:
            if ssend[-8:].upper() != checksum(ssend[:-8]):
                print ('Invalid sender\'s checksum')
                return (False)
        if srec[-8:].upper() != checksum(srec[:-8]):
                print ('Invalid recepient\'s checksum')
                return (False)
    except ValueError:
        print ('Invalid address format, it must be base58')
        return (False)
    #print ('Both addresses are available')
    return (True)

def check_address(trans):
    if (trans.sender == '0' * 34):
        return (True)
    if len(trans.public_address) != 128:
        print ('Wrong length of public address in transaction')
        return (False)
    s = trans.public_address
    x = s[:64]
    y = s[64:]
    s = ('03' if int(y[63], 16) & 1 else '02') + x
    sha = hashlib.sha256(binascii.unhexlify(s)).hexdigest().upper()
    h = hashlib.new('ripemd160')
    h.update(binascii.unhexlify(sha))
    s = '00' +  h.hexdigest()
    sha1 = hashlib.sha256(binascii.unhexlify(s)).hexdigest().upper()
    sha2 = hashlib.sha256(binascii.unhexlify(sha1)).hexdigest().upper()
    s += sha2[0:8]
    s = s.upper()
    s = base58.b58encode(binascii.unhexlify(s)).decode()
    if (trans.sender != '0' * 34):
        if (s != trans.sender):
            print ('Sender\'s address doesn\'t match with public key from transaction')
            return (False)
    #print ('Sender\'s address mathes')
    return (True)

def check_valid(trans):
    res = verify(trans.public_address, trans.signature, trans.gethash())
    #print('Signature matches' if res else 'Signatures doesn\'t match')
    return (res)

def verification(trans):
    return check_aval(trans) and check_address(trans) and check_valid(trans)

