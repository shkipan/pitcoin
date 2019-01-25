import sys
from transaction import Transaction
from tx_validator import verification

class Serializer():

    def serialize(trans):
        l1 = '%04x' % trans.amount
        s1 = '0' * (35  - len(trans.sender)) + trans.sender
        s2 = '0' * (35  - len(trans.recipient)) + trans.recipient
        result = l1 + s1 + s2 + trans.public_address + trans.signature
        print (result)
        return (result)

class Deserializer():

    def deserialize(result):
        amount = int(result[0:4], 16)
        sender = str(result[5:39])
        recipient = str(result[40:74])
        if (sender != '0' * 34):
            sender = sender.replace('0', '')
        recipient = recipient.replace('0', '')
        pa = result[74:202]
        sign = result[202:]
        x = Transaction(sender, recipient, amount)
        x.public_address = pa
        x.signature = sign
        return (x)

