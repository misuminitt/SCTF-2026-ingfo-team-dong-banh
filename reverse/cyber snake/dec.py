def main():
    encrypted_hex = (
        "1323342612161b130e140b133f23500e"
        "13500c340e33280c3413141350120f011b"
    )
    encrypted = bytes.fromhex(encrypted_hex)
    decrypted = bytes()
    for b in encrypted:
        decrypted += bytes([b ^ 0x60])
    print("Raw decrypted flag:")
    print(decrypted.decode(errors="replace"))
    inner = decrypted.decode(errors="replace")
    flag_content = inner.split("{", 1)[1].rstrip("{")
    final_flag = f"SCTF26{{{flag_content}}}"
    print("Final flag:")
    print(final_flag)
if __name__ == "__main__":
    main()
