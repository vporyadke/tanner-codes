from correct import correct_errors, is_valid
import bchlib
import random
import sys

def read_graph(filename):
    f = open(filename, "r")
    inv = list(map(int, f.readline().split()))
    g = []
    for line in f.readlines():
        g.append(list(map(int, line.split())))
    f.close()
    return inv, g

def bitflip(packet):
    byte_num = random.randint(0, len(packet) - 1)
    bit_num = random.randint(0, 7)
    packet[byte_num] ^= (1 << bit_num)

p, q = 461, 29
t = 1839
inv, g = read_graph("461_29.graph")
n = q * (q * q - 1)
d = p + 1
data = bytearray(n * d // 8)
bch = bchlib.BCH(0x211, 50)
print(is_valid(data, bch, n, d, g, inv))
for _ in range(10):
    corrupted = data.copy()
    errs = random.randint(1, 2 * t)
    for i in range(errs):
        bitflip(corrupted)
    print(f"{errs} errors, does it work?")
    restored = correct_errors(corrupted, bch, n, d, g, inv)
    print(data == restored)
    #print(is_valid(corrupted, bch, n, d, g, inv), is_valid(restored, bch, n, d, g, inv))
    sys.stdout.flush()
        

