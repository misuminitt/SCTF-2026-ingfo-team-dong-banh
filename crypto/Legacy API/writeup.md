# Legacy API — Writeup

**Category    :** Crypto  
**Difficulty  :** Medium  
**File        :** legacy_api.txt   
**Description :**

Legacy signing service leaked enough information to recover the secret.

## Solve

Dari file challenge terlihat bahwa kita diberi banyak signature `ECDSA` pada kurva `SECP256k1`. Petunjuk paling penting ada di bagian atas file

```text
ECDSA Signatures (Curve: SECP256k1)
Notice: The top 8 bits of the nonce 'k' are always zero due to a faulty RNG.
DEBUG_LOG: Flag wrapped securely. Key derived using sha256(string(private_key))
```

Kalimat `top 8 bits of the nonce k are always zero` langsung menunjukkan bahwa nonce ECDSA yang dipakai bersifat bias. Dalam ECDSA, kalau nonce `k` tidak benar-benar acak, private key bisa dipulihkan dari kumpulan signature menggunakan serangan lattice

Jadi dari awal sudah ada dua bagian challenge ini

- pulihkan `private key` dari biased nonce ECDSA
- gunakan private key itu untuk membuka data flag yang sudah di-wrap

Format data pada `legacy_api.txt` berulang seperti ini

```text
Hash: 0xfcb18e905e1079554ffe483afcb050b787828b94d89fdf0307298543d3afddaf
r: 0xb5eb9c796567540a97582a8affb5c15eb8cdd3f4e0be6848f6cd2ec196b1d639
s: 0xbe401cc1c7d15c276c495744a5a1ac3d4083a46bea7f692e2d2df44dbaab9f79
```

Karena 8 bit teratas dari nonce selalu nol, berarti setiap nonce memenuhi batas

- `k < 2^248`

Ini cukup untuk membangun lattice dari persamaan ECDSA

- `s = k^-1 (h + r*d) mod n`

Jika diubah, maka untuk kandidat private key `d` kita bisa menghitung kembali semua nonce dengan

- `k = (h + r*d) * s^-1 mod n`

Private key yang benar akan menghasilkan nonce-nonce yang semuanya berada di bawah batas `2^248`

Karena itu, yang akan ku coba adalah memakai `LLL` untuk memulihkan kandidat `d`, lalu memverifikasi bahwa semua nonce hasil rekonstruksi memang memenuhi syarat bias tadi

Tapi challenge ini tidak selesai hanya dengan dapat `d`. Ada petunjuk tambahan

- `Key derived using sha256(string(private_key))`

Artinya setelah private key ketemu, key simetris dibentuk dari

- `sha256(str(d)).digest()`

Lalu data hex dari prompt web ternyata adalah ciphertext AES. Dari solve yang benar, ciphertext itu diproses sebagai `AES-ECB`, kemudian di-unpad untuk memperoleh flag

Solver yang kupakai ada di `final_solve.py`

final_solve.py
```python
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
```

output
```text
private_key = 0x6d62d195bc8fb534bb898f6b25478b1c4b6852af5238bf85a24b1209ca562a3e
derived_sha256 = 77ddace8dbf776a541d7ff14ba3ad47c5b7364471e6baa347a28eb36105cdd43
flag = SCTF26{3d662943827ce627c2101ef864b41f24fe2496bb81654469caa6ab68eedf8735}
```

## Flag

```text
SCTF26{3d662943827ce627c2101ef864b41f24fe2496bb81654469caa6ab68eedf8735}
```
