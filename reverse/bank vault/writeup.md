# Bank Vault — Writeup

**Category    :** Reverse  
**Difficulty  :** Medium  
**File        :** bank_vault.zip   
**Description :**

An ATM simulation with a custom encryption algorithm for the PIN.

## Solve

Pertama kita unzip `bank_vault.zip` dan coba di beri premission execute

```
unzip bank_vault.zip -d bank_vault
```

Lalu kita cek hasil unzip ada apa saja dan kita coba cek dengan `file`

```
ls -la bank_vault

file bank_vault/*
```

output
```
total 32
drwxr-xr-x  3 ridwankusumahani  staff     96 Jul  4 01:55 .
drwxr-xr-x  8 ridwankusumahani  staff    256 Jul  4 01:55 ..
-rwxr-xr-x@ 1 ridwankusumahani  staff  14456 Jun 27 19:25 bank_vault

bank_vault/bank_vault: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=28b3b1983061b4301444f78bfadb4b9dc39e4671, for GNU/Linux 3.2.0, stripped
```

Ternyata hasil dari `file` adalah file executable, lalu kita coba `chmod +x bank_vault` lalu baru `strings` untuk melihat isinya

```
chmod +x bank_vault

strings bank_vault/bank_vault | grep -iE "flag|pin|vault|SCTF|granted|denied"
```

output
```
--- SCTF Secure Bank ATM ---
Enter 8-digit master PIN: 
Invalid PIN length!
Access Granted!
Flag: SCTF26{w3lc0m3_t0_th3_v4ult_p1n_%lld}
Access Denied.
```

Kita mendapat flag awalnya, namun masih ada yang janggal yaitu `%lld`, itu adalah yang akan diganti dengan nilai PIN yang di masukan dengan `printf`. Kita coba cek `objdump` untuk melihat assembly nya

```
objdump -d -M intel bank_vault/bank_vault | less
```

output bagian penting
```
bank_vault/bank_vault: file format elf64-x86-64

Disassembly of section .text:

0000000000001185 <encrypt_pin>:
    1185: 55                            push   rbp
    1186: 48 89 e5                      mov    rbp, rsp
    1189: 48 89 7d e8                   mov    qword ptr [rbp - 0x18], rdi
    118d: 48 89 75 e0                   mov    qword ptr [rbp - 0x20], rsi

    1191: b8 ef be ad de                mov    eax, 0xdeadbeef
    1196: 48 89 45 f8                   mov    qword ptr [rbp - 0x8], rax

    119a: b8 be ba fe ca                mov    eax, 0xcafebabe
    119f: 48 89 45 f0                   mov    qword ptr [rbp - 0x10], rax

    11a3: 48 8b 45 e8                   mov    rax, qword ptr [rbp - 0x18]
    11a7: 48 33 45 f8                   xor    rax, qword ptr [rbp - 0x8]
    11ab: 48 69 c0 39 05 00 00          imul   rax, rax, 0x539
    11b2: 48 33 45 f0                   xor    rax, qword ptr [rbp - 0x10]

    11b6: 48 89 c2                      mov    rdx, rax
    11b9: 48 8b 45 e0                   mov    rax, qword ptr [rbp - 0x20]
    11bd: 48 89 10                      mov    qword ptr [rax], rdx
    11c1: 5d                            pop    rbp
    11c2: c3                            ret
```

Hasil dari objdump terlihat menjadi sebuah rumus `encrypted = ((pin ^ 0xdeadbeef) * 0x539) ^ 0xcafebabe;`, maka kita bisa membuat solver nya seperti ini

pin.py
```
target = 0x48cf6ea6484
xor1 = 0xdeadbeef
xor2 = 0xcafebabe
mul = 0x539
mod = 1 << 64

inv = pow(mul, -1, mod)
pin = ((target ^ xor2) * inv % mod) ^ xor1

print(pin)
print(f"SCTF26{{w3lc0m3_t0_th3_v4ult_p1n_{pin}}}")
```

output
```
9147487905852048613
SCTF26{w3lc0m3_t0_th3_v4ult_p1n_9147487905852048613}
```

## Flag

```text
SCTF26{w3lc0m3_t0_th3_v4ult_p1n_9147487905852048613}
```
