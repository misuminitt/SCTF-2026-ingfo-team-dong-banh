
target = 0x48cf6ea6484

xor1 = 0xdeadbeef

xor2 = 0xcafebabe

mul = 0x539

mod = 1 << 64

inv = pow(mul, -1, mod)

pin = ((target ^ xor2) * inv % mod) ^ xor1

print(pin)

print(f"SCTF26{{w3lc0m3_t0_th3_v4ult_p1n_{pin}}}")

