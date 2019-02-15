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
            vk.verify(bytes.fromhex(signature[:-2]), bytes.fromhex(stack.trans_hex))#, sigdecode=ecdsa.util.sigdecode_der_canonize)
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

    def __init__(self, he, muted=True):
        self.validity = True
        self.muted=True
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
            print ('/', i)
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
                    if not stack.muted:
                        stack.display()
                    code[2](stack, stack.pop())
                    code_done = True
                    break
            if not code_done:
                x = script[i + 1 : i + elem + 1]
                stack.push(x.hex())
                i += elem 
            i += 1
        return True, 'Script is valid'
        

           

if __name__ == '__main__':
    scriptsig = '41289a5d2e0a373d2bc37713043f806290f28ecc7f5bb334011183fdec8e87bc7279b341f57e4a54bf76a89ec70873f7c6eaec6a7d02de8ccc6022872e6d96aa7f0141040bd6af4572a569e8c512f686cd5b9f414a58b71cf1a54543b20afdbe9129b9693b6b37493a4c5b8d716d2d93e5d34f9bd39753db8ecd59d9ec89b23dbf5ffdb1'
    script = '76a91432ecbb1b78a870466ed165d98165fba6ddb3828488ac'
    scr = Script('1f0b671930cf4d72983f8974c0ec6893a96c4202283e6d5b6271cec7d5497982')
    print (scr.decode(script, scriptsig))

 
