
def bech(s):
    x = ''

    for i in s:
        x += '{0:08b}'.format(i)
    arr = [x[i: i + 5] for i in range(0, len(x), 5)]
    s = ''
    for i in arr:
        s += '{:02x}'.format(int(i, 2))
    s = '00' + s
    print (s)




if __name__ == '__main__':
    bech(bytes.fromhex('751e76e8199196d454941c45d1b3a323f1433bd6'))

