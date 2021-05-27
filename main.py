from correct import correct_errors, is_valid
import bchlib
import random
import sys

def read_graph(filename):
    f = open(filename, "r")
    inv = list(map(int, f.readline().split()))
    psl = list(map(int, f.readline().split()))
    g = []
    for line in f.readlines():
        g.append(list(map(int, line.split())))
    f.close()
    n = len(g)
    non_psl = []
    j = 0
    for i in range(n):
        if psl[j] == i:
            j += 1
        else:
            non_psl.append(i)
    v_nums = dict()
    for i in range(len(psl)):
        v_nums[psl[i]] = i
    return g, psl, non_psl, inv, v_nums

def bitflip(packet, i):
    byte_num = i // 8
    bit_num = i % 8
    packet[byte_num] ^= (1 << bit_num)

p, q = 461, 29
t = 1839
g, psl, non_psl, inv, v_nums = read_graph("461_29.graph")
psl_set = set(psl)
n = q * (q * q - 1)
d = p + 1
data = bytearray(n * d // 16)
bch = bchlib.BCH(0x211, 27)
assert is_valid(data, bch, n, d, g, psl, non_psl, inv, v_nums)
l = 9000
r = 260000

def corrupt(packet, max_errs):
    errs = random.randint(min(28, max_errs), min(d, max_errs))
    v_num = random.randint(0, n - 1)
    flips = random.sample(range(d), errs)
    for flip in flips:
        i = v_nums[v_num] * d + flip if v_num in psl_set else v_nums[g[v_num][flip]] * d + inv[flip]
        bitflip(packet, i)
    return errs


while r == None or r - l > 1:
    m = l * 2 if r == None else (r + l) // 2
    fl = True
    print(f"{m} errors, does it work?")
    for iter in range(500):
        corrupted = data.copy()
        errs_left = m
        while errs_left > 0:
            errs_left -= corrupt(corrupted, errs_left)
        restored = correct_errors(corrupted, bch, n, d, g, psl, non_psl, inv, v_nums)
        if data != restored:
            fl = False
            break
    print(fl)
    if fl:
        l = m
    else:
        r = m
        

