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
        sha = hashlib.sha256(bytes.fromhex(item)).digest()
        h = hashlib.new('ripemd160')
        h.update(sha)
        s = h.hexdigest()
        stack.push(s)
        return (s)

    def check(stack, pubk):
        signature = stack.pop()

        '''
        vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(public_key), curve=ecdsa.SECP256k1)
        try:
            vk.verify(bytes.fromhex(signature), bytes.fromhex(stack.trans_hex), sigdecode=ecdsa.util.sigdecode_der)
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
    def display(self):
        print (wallet.termcolors.RED + '_____________________' + wallet.termcolors.DEF)
        for i in self.items:
            print ('࿈', i)
        print (wallet.termcolors.RED + '_____________________' + wallet.termcolors.DEF)

    def decode(self, script, scriptpubkey):
        stack = self
        Script.verify_script(stack, scriptpubkey)
        Script.verify_script(stack, script)
        return (stack.pop())

    def verify_script(stack, script):
        if not script:
            return False, 'Invalid tx_prev_hash'
        script = bytes.fromhex(script)
        i = 0
        while i < len(script):
            code_done = False
            elem = script[i]
            for code in Script.operations:
                if (elem == code[0]):
                 #   print (code[1])
                    code[2](stack, stack.pop())
                 #   stack.display()
                    code_done = True
                    break
            if not code_done:
                x = script[i + 1 : i + elem + 1]
                stack.push(x.hex())
             #  stack.display()
                i += elem 
            i += 1
        return True, 'Script is valid'
        

           

if __name__ == '__main__':
    scriptsig = '483045022100f2fd091947e9f07d8de42efe18ee8471f98edebdf0684da535c69584d29ea27e022076818b93dfb10e43ab2167e31d6c61c8e6abaef5ec383eabdec7a5e3151184d10121030bd6af4572a569e8c512f686cd5b9f414a58b71cf1a54543b20afdbe9129b969'
    script = '76a9149ee1c9c57e86f8d1264a02f8af8a5c2543f787bc88ac'
    scr = Script('8b367538abb9e099d9e3e902d566defed0485eeaafdba0d7bdf70fe4c4afa6bc')
    print (scr.decode(script, scriptsig))

 
