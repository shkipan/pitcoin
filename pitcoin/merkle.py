import sys, hashlib

def merkle_root(t):
    transs = []
    for i in t:
        transs.append(i)
    if len(transs) & 1:
          transs.append(transs[len(transs) - 1])
  #  print (t)
    while (len(transs) > 1):
        res = []
        for i in range(int(len(transs) / 2)):
            h1 = hashlib.sha256(bytes(transs[2 * i], 'utf-8')).hexdigest().upper()
            h2 = hashlib.sha256(bytes(transs[2 * i + 1], 'utf-8')).hexdigest().upper()
            res.append(h1 + h2)
        transs = res
        if len(transs) & 1 and len(transs) != 1:
            transs.append(transs[len(transs) - 1])
    return (hashlib.sha256(bytes(transs[0], 'utf-8')).hexdigest().upper())

def main():
    s = [str(i) for i in range(9)]
    for i in s:
        print (hashlib.sha256(bytes(i, 'utf-8')).hexdigest().upper())
    print ('________________')
    print (merkle_root(s))

if __name__ == '__main__':
    main()
