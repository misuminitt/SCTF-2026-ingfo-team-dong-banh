# Low Entropy — Writeup

**Category    :** Crypto  
**Difficulty  :** Medium  
**File        :** 4_low_entropy.txt   
**Description :**

Two entities generated their RSA keys at the exact same time on a cloud provider with low entropy.

## Solve

Dari file challenge kita diberi `N`, `e`, `C`, dan bocoran bit dari `p`. Jadi sejak awal sudah terlihat kalau challenge ini bukan RSA biasa yang harus difaktorkan dari nol, karena salah satu prime factor sudah hampir diketahui.

Isi file chall

```text
N = 80329589900848116233988882207375979703121859486146305045816492666964968431294552070408716008243121191783239071478515627573994596834773273847417073356518568709416991168147566693847145648646025262320546610493721479789958890761574201773327276539921327394182396030193653421455891376888536611596300960119551975757
e = 65537
C = 10727007459887951081038288006334718838121029247037460588430504700466653165041190727066716664156880960559125796752321978327460646167339985445249541182663517597078602662671105431479469194649714951502904638070509652906007703481647501664723560678352827805551279409891077312786523091521032575731473451504693476715

Leaked p (binary): 100001100000011010011000010100100111100010011011101010011110101110010101000011011111100011000011110011010010110010010111011110011100101111101001101100????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????100011010100100010100001110010111000101010000101100011111001000011001010000101001100100010101101101100000010000010110010001101001000011110010111001011000010010001
```

Kalau dilihat, bentuk `p` hanya memiliki dua bagian tetap dan satu bagian hilang di tengah. Artinya pola bocornya adalah

- `prefix`
- `200 bit` yang tidak diketahui
- `suffix`

Jadi bentuk matematisnya bisa ditulis sebagai

- `p = prefix || unknown_bits || suffix`
- `p = known + x * 2^(suffix_bits)`

Di sini

- `known` adalah bagian prefix dan suffix yang sudah diketahui
- `x` adalah nilai 200 bit yang hilang

Karena hanya bagian tengah yang hilang, maka ini bukan brute force biasa. Kalau dicoba brute force, ruang pencariannya adalah `2^200`, yang jelas mustahil. Maka pendekatan yang cocok adalah `Coppersmith small roots`, karena kita mencari akar kecil dari polinomial modular yang dibentuk dari faktor RSA tersebut.

Karena `p` membagi `N`, maka kita bisa bentuk polinomial

- `f(x) = known + shift * x (mod N)`

Dengan `shift = 2^(suffix_bits)`. Nilai `x` yang benar harus membuat `f(x)` menjadi faktor dari `N`.

Karena itu, yang akan ku coba adalah memakai SageMath untuk mencari nilai `x` kecil tersebut menggunakan `small_roots()`.

solver.py
```python
from sage.all import PolynomialRing, Zmod
from pathlib import Path
import re


def long_to_bytes(value: int) -> bytes:
    if value == 0:
        return b"\x00"
    length = (value.bit_length() + 7) // 8
    return value.to_bytes(length, "big")


def parse_challenge(path: str = "4_low_entropy.txt"):
    text = Path(path).read_text()
    modulus = int(re.search(r"N = (\d+)", text).group(1))
    exponent = int(re.search(r"e = (\d+)", text).group(1))
    ciphertext = int(re.search(r"C = (\d+)", text).group(1))
    leak = re.search(r"Leaked p \(binary\): ([01?]+)", text).group(1)
    return modulus, exponent, ciphertext, leak


def main():
    modulus, exponent, ciphertext, leak = parse_challenge()

    prefix_bits = leak.split("?")[0]
    suffix_bits_str = leak.split("?")[-1]
    unknown_bits = leak.count("?")
    suffix_length = len(suffix_bits_str)

    prefix = int(prefix_bits, 2)
    suffix = int(suffix_bits_str, 2)

    known = (prefix << (unknown_bits + suffix_length)) + suffix
    shift = 2 ** suffix_length
    bound = 2 ** unknown_bits

    ring = PolynomialRing(Zmod(modulus), "x")
    x = ring.gen()
    polynomial = known + shift * x

    print(f"[+] unknown bits: {unknown_bits}")
    print(f"[+] suffix bits : {suffix_length}")
    print("[+] running Coppersmith / small_roots...")

    roots = polynomial.small_roots(X=bound, beta=0.5)
    if not roots:
        raise SystemExit("[-] root tidak ditemukan")

    missing = int(roots[0])
    prime_p = known + missing * shift
    prime_q = modulus // prime_p

    if prime_p * prime_q != modulus:
        raise SystemExit("[-] faktorisasi gagal")

    phi = (prime_p - 1) * (prime_q - 1)
    private_exponent = pow(exponent, -1, phi)
    plaintext = pow(ciphertext, private_exponent, modulus)
    flag = long_to_bytes(plaintext)

    print(f"[+] missing bits value: {missing}")
    print(f"[+] p: {prime_p}")
    print(f"[+] q: {prime_q}")
    print(f"[+] flag: {flag.decode()}")


if __name__ == "__main__":
    main()
```

Karena script ini memakai `sage.all`, maka cara menjalankannya adalah dengan interpreter dari Sage.

```bash
sage -python solver.py
```

output
```text
[+] unknown bits: 200
[+] suffix bits : 162
[+] running Coppersmith / small_roots...
[+] flag: SCTF26{c0mm0n_f4ct0r_4tt4ck_ru1n5_r54_53cur1ty}
```

## Flag

```text
SCTF26{c0mm0n_f4ct0r_4tt4ck_ru1n5_r54_53cur1ty}
```
