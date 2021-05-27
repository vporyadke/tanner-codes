import numpy as np

# Finds a square root of -1 modulo q
def find_j(q):
    for i in range(q):
        if i * i % q == q - 1:
            return i


def get_matrix(a, j, q):
    return np.array([[a[0] + j * a[1], a[2] + j * a[3]],
                     [-a[2] + j * a[3], a[0] - j * a[1]]]) % q

def find_generating_set(p, q):
    j = find_j(q)
    # Search for solutions to a_0^2 + a_1^2 + a_2^2 + a_3^2 = p
    # There are 8(p + 1) of them, restrict parity and signs to only get p + 1
    s = []
    for a0 in range(1, p, 2):
        acc0 = a0 * a0
        if acc0 > p:
            break
        for a1 in range(0, p, 2):
            acc1 = acc0 + a1 * a1
            if acc1 > p:
                break
            for a2 in range(0, p, 2):
                acc2 = acc1 + a2 * a2
                if acc2 > p:
                    break
                for a3 in range(0, p, 2):
                    acc3 = acc2 + a3 * a3
                    if acc3 > p:
                        break
                    if acc3 == p:
                        a = [a0, a1, a2, a3]
                        # Go through all options on a1, a2, a3 signs
                        # Do not create duplicates when ai = 0
                        for sign_mask in range(1 << 3):
                            b = a.copy()
                            valid = True
                            for i in range(3):
                                if (sign_mask & (1 << i)) == 0:
                                    continue
                                if b[i + 1] == 0:
                                    valid = False
                                    break
                                b[i + 1] *= -1
                            if valid:
                                s.append(get_matrix(b, j, q))


    return s

# We will consider A a canoncial representation of a projective linear map if
# the first nonzero value of A.flatten() is 1

def power(a, n, mod):
    if n == 0:
        return 1
    r = power(a, n // 2, mod)
    return r * r * (a if n % 2 != 0 else 1) % mod

def inverse(a, mod):
    return power(a, mod - 2, mod)

# writes all elements of PGL(2, Z_q) as quadruples into the given file
def write_pgl(q, filename):
    def nxt(A):
        j = 1
        while True:
            A[-j] = (A[-j] + 1) % q
            if A[-j] != 0:
                break
            j += 1

    cur = 0
    psl = []
    f = open(filename, "w")
    for i in range(2):
        A = np.zeros((4), dtype=int)
        A[i] = 1
        while True:
            d = round(np.linalg.det(A.reshape((2, 2)))) % q 
            if d != 0:
                print(*A, file=f)
                if power(d, (q - 1) // 2, q) == 1:
                    psl.append(cur)
                cur += 1
            nxt(A)
            if A[i] != 1:
                break
    print(*psl, file=f)
    f.close()

def make_canon(A, q):
    f = A[0, 0] if A[0, 0] != 0 else A[0, 1]
    return (A * inverse(f, q)) % q

# computes a permutation pi corresponding to taking inverses, i. e.
# pi(i) = j => s[i]^-1 = s[j]
def get_inverses(s, q):
    pi = [0] * len(s)
    getNum = dict()
    for i in range(len(s)):
        getNum[tuple(make_canon(s[i], q).flatten())] = i

    for i in range(len(s)):
        det = round(np.linalg.det(s[i]))
        inv = np.array([[s[i][1, 1], -s[i][0, 1]],
                        [-s[i][1, 0], s[i][0, 0]]]) * inverse(det, q) % q
        pi[i] = getNum[tuple(make_canon(inv, q).flatten())]
    return pi

# writes graph in the following format:
# the inversion permuation
# numbers of elements that are in PSL
# adjacency list, one line per vertex
def write_graph(p, q, pgl_file, filename):
    getNum = dict()
    pgl = []
    fin = open(pgl_file, "r")
    for i in range(q * (q ** 2 - 1)):
        line = fin.readline()
        a = tuple(map(int, line.split()))
        getNum[a] = len(pgl)
        pgl.append(np.array(a).reshape((2, 2)))
    psl = list(map(int, fin.readline().split()))
    fin.close()

    fout = open(filename, "w")
    s = find_generating_set(p, q)
    inv = get_inverses(s, q)
    print(*inv, file=fout)
    print(*psl, file=fout)
    for u in pgl:
        adj = []
        for edge in s:
            v = make_canon(u @ edge % q, q)
            adj.append(getNum[tuple(v.flatten())])
        print(*adj, file=fout)
