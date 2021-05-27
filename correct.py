import bchlib

def correct_errors(data, bch, n, d, g, psl, non_psl, inv, v_nums):
    def get_barr(arr, i):
        return (arr[i // 8]  & (1 << (i % 8))) >> (i % 8)

    def set_barr(arr, i, v):
        if v == 0:
            arr[i // 8] &= 0xff - (1 << (i % 8))
        else:
            arr[i // 8] |= (1 << (i % 8))

    def bch_decode(arr):
        bitflips, data, ecc = bch.decode(arr[:-bch.ecc_bytes], arr[-bch.ecc_bytes:])
        return bitflips, data + ecc

    prev = bytearray(len(data))
    cur = data.copy()
    i = 0
    # For some reason, bchlib requests more ecc bytes than it uses, account for that
    bch_pad = (8 * bch.ecc_bytes - bch.ecc_bits - 1) // 8 + 1
    while i < 2 or prev != cur:
        prev = cur
        part = psl if i % 2 == 0 else non_psl
        for u in part:
            word = bytearray(d // 8 + 1 + bch_pad)
            edges = [0] * d
            for (j, v) in enumerate(g[u]):
                edges[j] = v_nums[u] * d + j if i % 2 == 0 else v_nums[v] * d + inv[j]
                val = get_barr(prev, edges[j])
                set_barr(word, j, val)
            flips, decoded_word = bch_decode(word)
            if flips == 0:
                continue
            for j in range(d):
                val = get_barr(decoded_word, j)
                set_barr(cur, edges[j], val)
        i += 1
        if i > 40:
            print('failed to converge')
            break
    print(f"{i} iters")
    return cur

def is_valid(data, bch, n, d, g, psl, non_psl, inv, v_nums):
    def get_barr(arr, i):
        return (arr[i // 8]  & (1 << (i % 8))) >> (i % 8)

    def set_barr(arr, i, v):
        if v == 0:
            arr[i // 8] &= 0xff - (1 << (i % 8))
        else:
            arr[i // 8] |= (1 << (i % 8))

    def bch_decode(arr):
        bitflips, data, ecc = bch.decode(arr[:-bch.ecc_bytes], arr[-bch.ecc_bytes:])
        return bitflips, data + ecc

    bch_pad = (8 * bch.ecc_bytes - bch.ecc_bits - 1) // 8 + 1
    for i in range(2):
        checked = set()
        part = psl if i % 2 == 0 else non_psl
        for u in part:
            word = bytearray(d // 8 + 1 + bch_pad)
            edges = [0] * d
            for (j, v) in enumerate(g[u]):
                edges[j] = v_nums[u] * d + j if i % 2 == 0 else v_nums[v] * d + inv[j]
                val = get_barr(data, edges[j])
                checked.add(edges[i])
                set_barr(word, j, val)
            flips, decoded_word = bch_decode(word)
            if flips != 0:
                return False
    return True

