import sys
from serializer import Deserializer
from tx_validator import verification

import urllib.request, json, requests


def add_trans(plain):
    x = Deserializer.deserialize(plain)
    if not verification(x):
        print ('Error, serialization of transaction failed')
    else:
        save_to_mem(x, plain)

 #   if not verification(x):
 #       save_to_mem(x, plain)

def save_to_mem(trans, plain):
    f = open('mempool', 'a+')
    send_url = 'http://127.0.0.1:5000/transactions/new'
    data = {
        'sender': trans.sender,
        'recipient': trans.recipient,
        'amount': trans.amount,
    }
    r = requests.post(url = send_url, json=data)

    f.write(plain+'\n')
    f.close()

def get_trans():
    try:
        f = open('mempool', 'r+')
    except IOError:
        print ('No mempool file')
        return None 
    s = f.read().split('\n')[-4:-1]
    f.close()
    if (len(s) == 0):
        print ('mempool is empty')
    for trans in s:
        Deserializer.deserialize(trans).display()
    
    with urllib.request.urlopen('http://127.0.0.1:5000/transactions') as url:
        data = json.loads(url.read().decode())
        for i in data['ppool']:
            print (i['sender'], i['recipient'])
            print (i['amount'])
    return (s)


if __name__ == '__main__':
    get_trans()
