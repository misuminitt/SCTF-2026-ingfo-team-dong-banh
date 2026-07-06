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
