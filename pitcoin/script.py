#processing bitcoin script data
import binascii, hashlib, ecdsa, math
import wallet

class Script():

    def verify(stack, item):
        if not item:
            stack.validity = False
            return False
        return True

    def dup(stack, item):
        stack.push(item)
        stack.push(item)
        return (item)

    def has(stack,item):
        item = bytes.fromhex('030bd6af4572a569e8c512f686cd5b9f414a58b71cf1a54543b20afdbe9129b969')
        sha = hashlib.sha256(item).digest()
        h = hashlib.new('ripemd160')
        print (sha)
        h.update(sha)
        s = h.hexdigest()
        stack.push(s)
        print (wallet.termcolors.RED + 'fin', s + wallet.termcolors.DEF)
        return (s)

    def check(stack, pubk):
        sig = stack.pop()
        p_hex = 'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F'
        p = int(p_hex, 16)
        x_hex = pubk[2:]
        x = int(x_hex, 16)
        y_sq = (pow(x, 3, p)  + 7) % p
        y = pow(y_sq, int((p+1)/4), p)
        print ('y=', y)
        if (y & 1 == 1 and x_hex[0:2] == '03') or (y & 1 == 0 and x_hex[0:2] == '02'):
            y = y
        else:
            y = (-1 * y) % p


   
        '''
        vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(pubk), curve=ecdsa.SECP256k1)
        try:
            vk.verify(bytes.fromhex(sig), bytes.fromhex(stack.trans_hex), sigdecode=ecdsa.util.sigdecode_der)
            print ('Valid Sig')
            stack.validity = True
        except ecdsa.BadSignatureError:
            print ('Invalid Sig')
            stack.validity = False
        '''
        stack.push(True)
        return True

    def equ(stack, item):
        item2 = stack.pop()
        print (item)
        print (item2)
        stack.push(False if item != item2 else True)
        return Script.verify(stack, stack.pop()) 

    operations = [
            [118, 'OP_DUP', dup],
            [169, 'OP_HASH160', has],
            [172, 'OP_CHECKSIG', check],
            [136, 'OP_EQUALVERIFY', equ],
    ]

    def __init__(self, he):
        self.validity = True
        self.trans_hex = he
        self.items = []

    def isEmpty(self):
        return self.items == []
    def push(self, item):
        self.items.append(item)
    def pop(self):
        return self.items.pop()
    def size(self):
        return len(self.items)
    def get(self):
        return (self.items)

    def decode(self, script, keys):
        stack = Script(self.trans_hex)
        for i in keys:
            stack.push(i)
        s = binascii.unhexlify(script)
        code = 0
        while (code < len(s)):
            op_done = False
            for i in Script.operations:
                if i[0] == s[code]:
                    op_done = True
                    i[2](stack, stack.pop())
            if not op_done:
                step = s[code]
                if code + step + 1 >= len(s):
                    return False
                res = s[code + 1: code + step + 1]
                stack.push(binascii.hexlify(res).decode())
                code += step
            print (stack.items)
            code += 1
        return stack.validity
    
    def encode(self, script):
        result = ''
        script = script.split(' ')
        for item in script:
            op_done = False
            for op in Script.operations:
                if op[1] == item:
                    op_done = True
                    result += hex(op[0]).replace('0x', '')
            if not op_done:
                result += hex(len(item)).replace('0x', '')
                result += item
        return result
        

if __name__ == '__main__':
    sig = '3045022100b30bacdd6e82125d1ab31c8e9e7f951dc881390f0723eddd396ec420cfe26e6f02205ae1fc04542b75f8b933b9e25efbc559c3a1f90a7864cdbc6f7ee22e9f1aecff'
    pub = '030bd6af4572a569e8c512f686cd5b9f414a58b71cf1a54543b20afdbe9129b969'
    print ('sig', sig)
    print ('pub', pub)
    script = Script('9ac980c2f590a0245875b7f97481da0f77251ce3f1120db401635130c1aee87f')
    print (script.decode('76a914e594a98386b8c08cb2b6714b4cd574147fc012a588ac', [sig, pub]))

 
