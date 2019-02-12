import sys
from serializer import Deserializer
from tx_validator import verification

import urllib.request, json, requests

from syncdata import get_config
from pathlib import Path

#home = str(Path.home()) + '/.pitcoin/'
home = './.pitcoin/'
my_url, PORT = get_config()

def add_trans(plain):
    x = Deserializer.deserialize(plain)
    save_to_mem(plain) if verification(x) else print ('Error, serialization of transaction failed')

def save_to_mem(plain):
    send_url = my_url + ':' + str(PORT) + '/transactions/new'
    data = {'serial': plain}
    try:
        r = requests.post(url = send_url, json=data)
    except requests.exceptions.ConnectionError:
        print ('Unable to connect')
        return False 
    d = json.loads(r.text)
    try:
        if (d['success']):
            return True
    except KeyError:
        print (d['error'] + ', transaction denied')
        return False 
    return True
   
def get_trans(data):
    s1 = []
    if (len(data['ppool']) == 0):
        return ''
    for i in data['ppool'][:3]:
        s1.append(i['serial'])
#        Deserializer.deserialize_raw(i['serial']).display_raw()
    return (s1)

def get_last_trans(data):
    s1 = []
    for i in data['ppool'][-3:]:
        s1.append(i['serial'])
#        Deserializer.deserialize(i['serial']).display()
    return (s1)

if __name__ == '__main__':
    get_trans()
