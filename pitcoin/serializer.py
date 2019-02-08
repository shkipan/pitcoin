import sys, binascii, struct, base58, hashlib, ecdsa
from transaction import Transaction
from wallet import sign, verify, termcolors, checksum

class bs:
    B = 1
    L = 4
    Q = 8
    SH = 32

def swap_bytes(s):
    flip = ''.join(reversed([s[i:i + 2] for i in range(0, len(s), 2)]))
    return (bytes.fromhex(flip))

class Deserializer():

    def deserialize(result):
        amount = int(result[0:4], 16)
        sender = str(result[5:39])
        recipient = str(result[40:74])
        if (sender != '0' * 35):
            sender = sender.replace('0', '')
        recipient = recipient.replace('0', '')
        pa = result[74:202]
        sign = result[202:]
        x = Transaction(sender, recipient, amount, None)
        x.public_address = pa
        x.signature = sign
        return (x)

    def deserialize_raw(result):
        trans_bytes = bytes.fromhex(result)
        version = struct.unpack('<L', trans_bytes[:bs.L])[0]
        trans_bytes = trans_bytes[bs.L:]
        tx_in_count = struct.unpack('<B', trans_bytes[:bs.B])[0]
        trans_bytes = trans_bytes[bs.B:]
        tx_inputs = []
        for i in range(tx_in_count):
            tx_prev_hash = swap_bytes(trans_bytes[:bs.SH].hex())
            trans_bytes = trans_bytes[bs.SH:]
            tx_prev_index = struct.unpack('<L', trans_bytes[:bs.L])[0]
            trans_bytes = trans_bytes[bs.L:]
            script_size  = struct.unpack('<B', trans_bytes[:bs.B])[0]
            trans_bytes = trans_bytes[bs.B:]
            script = trans_bytes[:script_size]
            trans_bytes = trans_bytes[script_size:]
            sequence = struct.unpack('<L', trans_bytes[:bs.L])[0]
            trans_bytes = trans_bytes[bs.L:]
            tx_inputs.append({
                'tx_prev_hash': tx_prev_hash.hex(),
                'tx_prev_index': tx_prev_index,
                'script': script.hex(),
                'sequence': sequence 
                })
        tx_out_count = struct.unpack('<B', trans_bytes[:bs.B])[0]
        trans_bytes = trans_bytes[bs.B:]
        tx_outputs = []
        for i in range(tx_out_count):
            value = struct.unpack('<Q', trans_bytes[:bs.Q])[0]
            trans_bytes = trans_bytes[bs.Q:]
            script_size  = struct.unpack('<B', trans_bytes[:bs.B])[0]
            trans_bytes = trans_bytes[bs.B:]
            script = trans_bytes[:script_size]
            trans_bytes = trans_bytes[script_size:]
            address = '6f' + script[3:-2].hex()
            address = base58.b58encode(bytes.fromhex(address + checksum(address))).decode()
            tx_outputs.append({
                'value': value,
                'address': address
                })
        lock_time = struct.unpack('<L', trans_bytes[:bs.L])[0]
        trans_bytes = trans_bytes[bs.L:]
        if len(trans_bytes) != 0:
            raise struct.error
        ext = {'inp': tx_inputs, 'oup': tx_outputs, 'locktime': lock_time, 'version': version}
        x = Transaction('', '', 0, ext)
        x.tr_hash = swap_bytes(hashlib.sha256(hashlib.sha256(bytes.fromhex(result)).digest()).hexdigest())
        return (x)

class Serializer():

    def serialize(trans):
        l1 = '%04x' % trans.amount
        s1 = '0' * (35  - len(trans.sender)) + trans.sender
        s2 = '0' * (35  - len(trans.recipient)) + trans.recipient
        result = l1 + s1 + s2 + trans.public_address + trans.signature
        print (result)
        return (result)

    @staticmethod
    def get_trans_for_sign(trans, index):
        v = struct.pack('<L', 1)
        tx_in_count = struct.pack('<B', trans.inputs_num)
        tx_in = []
        tx_out_count = struct.pack('<B', trans.outputs_num)
        for i in range(trans.inputs_num):
            item = trans.inputs[i]
            tx = {
                    'txouthash': swap_bytes(item['tx_prev_hash']),
                    'tx_out_index': struct.pack('<L', item['tx_prev_index']),
                    'script': bytes.fromhex(item['script']) if i == index else b'',
                    'script_bytes': struct.pack('<B', len(bytes.fromhex(item['script'])) if i == index else 0),
                    'sequence': struct.pack('<L', 0xffffffff)
            }
            tx_in.append(tx)
        tx_out = []
        for item in trans.outputs:
            hashed_pubk = base58.b58decode_check(item['address'])[1:]
            script = bytes.fromhex('76a914') + hashed_pubk + bytes.fromhex('88ac') 
            tx = {
                    'value': struct.pack('<Q', item['value']),
                    'pk_script': script,
                    'pk_script_bytes': struct.pack('<B', len(script))
            }
            tx_out.append(tx)
        raw_tx = v + tx_in_count 
        for i in tx_in:
            raw_tx += (
                    i['txouthash']
                    + i['tx_out_index']
                    + i['script_bytes']
                    + i['script']
                    + i['sequence']
            )
        raw_tx += tx_out_count
        for i in tx_out:
            raw_tx += (
                    i['value']
                    + i['pk_script_bytes']
                    + i['pk_script']
            )
        lock_time = struct.pack('<L', trans.timelock)
        raw_tx += lock_time + struct.pack('<L', 1)
        ret = hashlib.sha256(hashlib.sha256(raw_tx).digest()).digest()
        return ret, tx_in, tx_out


    def serialize_raw(trans, private_key, public_key):
        v = struct.pack('<L', 1)
        tx_in_count = struct.pack('<B', trans.inputs_num)
        tx_out_count = struct.pack('<B', trans.outputs_num)
        lock_time = struct.pack('<L', trans.timelock)

        txes_hashed_to_sign = []
        for i in range(trans.inputs_num):
            hashed_tx_to_sign, tx_in, tx_out = Serializer.get_trans_for_sign(trans, i)
            txes_hashed_to_sign.append(hashed_tx_to_sign)
        sk = ecdsa.SigningKey.from_string(bytes.fromhex(private_key), curve=ecdsa.SECP256k1)
        r_tx = v + tx_in_count 
        for index in range(len(tx_in)):
            i = tx_in[index]
            signature = sk.sign_digest(txes_hashed_to_sign[index], sigencode=ecdsa.util.sigencode_der_canonize)
            sigscript = (
                struct.pack('<B', len(signature) + 1)
                + signature
                + b'\01'
                + struct.pack('<B', len(bytes.fromhex(public_key)))
                + bytes.fromhex(public_key) 
            )
            i['script'] = sigscript
            i['script_bytes'] = struct.pack('<B', len(sigscript))
            r_tx += (
                    i['txouthash']
                    + i['tx_out_index']
                    + i['script_bytes']
                    + i['script']
                    + i['sequence']
            )
        r_tx += tx_out_count
        for i in tx_out:
            r_tx += (
                    i['value']
                    + i['pk_script_bytes']
                    + i['pk_script']
            )
        r_tx += lock_time
        return (r_tx)
     
if __name__ == '__main__':
    oup = [{'value': 800000, 'address': 'mv13YQAqcat77LVNVU2b8qh3GHiqCik6fi'}]
    inp = [{'tx_prev_hash':'01c12be1461a9eb63b3d04954a3f5d5e5e0445809724a335688a5a062c129fd8', 'tx_prev_index': 0, 'script': '76a9149ee1c9c57e86f8d1264a02f8af8a5c2543f787bc88ac'}]
    ext = {'inp': inp, 'oup':oup, 'locktime':0, 'version': 1}
    private_key = 'a106d38f79a67196e42202e679496235180390cb82f5639bd3cac91a20bc1d86'
    public_key = '030bd6af4572a569e8c512f686cd5b9f414a58b71cf1a54543b20afdbe9129b969'

    x = Transaction('','',10, ext)
 #   x.display_raw()
    raw = Serializer.serialize_raw(x, private_key, public_key)
    print ('////////////////////////////////////////')
    print (raw.hex())
    try:
        x = Deserializer.deserialize_raw(raw.hex())
#        x.display_raw()
    except struct.error:
        print ('Invalid length of raw transaction')
#    x.display()


