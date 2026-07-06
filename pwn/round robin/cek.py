#!/usr/bin/env python3
from pwn import *

elf = ELF("./chall")

print("[+] Binary info")
print("    Arch:", elf.arch)
print("    Bits:", elf.bits)
print("    PIE :", elf.pie)
print()

print("[+] Symbols")
if "win" in elf.symbols:
    print("    win =", hex(elf.symbols["win"]))
else:
    print("    win tidak ditemukan di symbols")

print()
print("[+] GOT")
for name in ["scanf", "__isoc99_scanf", "printf", "puts"]:
    if name in elf.got:
        print(f"    {name}@GOT =", hex(elf.got[name]))
