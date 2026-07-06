from pathlib import Path
import re
import hashlib
from ecdsa.curves import SECP256k1
from fpylll import IntegerMatrix, LLL
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

text = Path('../legacy_api.txt').read_text()
pat = re.compile(r'Hash: 0x([0-9a-f]+)\nr: 0x([0-9a-f]+)\ns: 0x([0-9a-f]+)', re.I)
sigs = [(int(h,16), int(r,16), int(s,16)) for h,r,s in pat.findall(text)]

n = SECP256k1.order
kbi = 2**8
limit = 2**256 // kbi

def inv(x):
    return pow(x, -1, n)

def build_matrix(subs):
    m = len(subs)
    M = IntegerMatrix(m + 2, m + 2)
    for i, (h, r, s) in enumerate(subs):
        M[i, i] = 2 * kbi * n
        M[m, i] = 2 * kbi * ((r * inv(s)) % n)
        M[m + 1, i] = 2 * kbi * (-h * inv(s)) + n
    M[m, m] = 1
    M[m + 1, m + 1] = n
    return M

def valid_count(d):
    ks = []
    for h, r, s in sigs:
        k = ((h + r * d) * inv(s)) % n
        ks.append(k)
    return sum(1 for k in ks if k < limit)

M = build_matrix(sigs)
LLL.reduction(M)
d = None
for row_idx in range(M.nrows):
    cand = M[row_idx, len(sigs)] % n
    for test in [cand, (n - cand) % n]:
        if test and valid_count(test) == len(sigs):
            d = test
            break
    if d:
        break

if not d:
    raise SystemExit('private key not found')

key = hashlib.sha256(str(d).encode()).digest()
wrapped = bytes.fromhex('d8a857f9499a36b2b08c4656f8d46a264b8a4f00987c60971eb6332a160131a2608b351b1ed39c70c41ae98f5a1d976c5d0acc6a9934ae55fb885b55961a4dbd75a09330e75734603ef73611a73a41dc')
pt = unpad(AES.new(key, AES.MODE_ECB).decrypt(wrapped), 16)

print('private_key =', hex(d))
print('derived_sha256 =', hashlib.sha256(str(d).encode()).hexdigest())
print('flag =', pt.decode())
