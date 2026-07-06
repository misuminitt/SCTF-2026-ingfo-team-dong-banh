# The Matryoshka Doll — Writeup

**Category    :** Forensics  
**Difficulty  :** Medium  
**File        :** the_matryoshka.png   
**Description :**

There is a secret deeply nested within. Can you uncover it? Note: The password is in plain sight.

## Solve

`Matryoshka` itu boneka Rusia yang isinya boneka lagi, jadi kemungkinan ada file tersembunyi di dalam file. Terus kalimat `password is in plain sight` berarti password mungkin terlihat di tempat yang mudah seperti metadata, strings, atau teks di gambar, namun ketika file gambar dibuka cuma putih dan berisi `Nothing to see here`. Jadi kita coba dengan `file the_matryoshka.png`

```
the_matryoshka.png: PNG image data, 800 x 600, 8-bit/color RGB, non-interlaced
```

Lalu kita cek dengan string di PNG `strings -a the_matryoshka.png`

```
IHDR
tEXtPassword
SCTF_EXIF_S3CR3T
IDATx
Ll3Xa
q>;0
Vz;M=
FY~4'_
paaa
];z8u
;6z8
dW\q
%3v`
3W^y
=sss
IEND
```

Ternyata terdapat `tEXtPassword` dan `SCTF_EXIF_S3CR3T`, berart clue nya benar kalau password tersmpan dan paswordnya `SCTF_EXIF_S3CR3T`. Selanjutnya ku coba `binwalk the_matryoshka.png`

![alt text](image.png)

Hasil dari binwalk tidak muncul sebagai append biasa. Jadi kemungkinan bukan file ditempel di akhir PNG, melainkan disembunyikan di pixel. Karena gambarnya putih polos, asumsi ku kalau tersembunyi nya menggunakan `LSB steganography`. Kita bikin script Python buat baca bit paling kecil dari tiap channel warna RGB, lalu cek apakah hasilnya membentuk file

pemecah.py
```
from PIL import Image
img = Image.open("the_matryoshka.png").convert("RGB")
pixels = list(img.getdata())
channels = {
    "red": 0,
    "green": 1,
    "blue": 2,
}
for name, idx in channels.items():
    bits = []
    for pixel in pixels:
        value = pixel[idx]
        bits.append(value & 1)
    data = bytearray()
    for i in range(0, len(bits), 8):
        byte_bits = bits[i:i+8]
        if len(byte_bits) < 8:
            break
        b = 0
        for bit in byte_bits:
            b = (b << 1) | bit
        data.append(b)
    outname = f"lsb_{name}.bin"
    with open(outname, "wb") as f:
        f.write(data)
    print(name, data[:16])
```

output
```
C:\Users\misuminitt\Downloads\SCTF\forens\the matryoshka\pemecah.py:3: DeprecationWarning: Image.Image.getdata is deprecated and will be removed in Pillow 14 (2027-10-15). Use get_flattened_data instead.
  pixels = list(img.getdata())
red bytearray(b'PK\x03\x04\x14\x00\x01\x00c\x00\x08l\xdb\\\x00\x00')
green bytearray(b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff')
blue bytearray(b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff')
```

Ternyata pada red bytearray terdapat zip tersembunyi, kita coba `mv lsb_red.bin hidden.zip` lalu kita cek `file hidden.zip`

```
hidden.zip: Zip archive data, compression method=AES Encrypted
```

Pada zip terdapat compression method=AES Encrypted, lalu kita coba cek isinya, tapi karna yang sebelumnya tidak memenuhi dari `480000 bit / 8 = 60000 byte`

```
from PIL import Image
import struct
img = Image.open("the_matryoshka.png").convert("RGB")
pixels = list(img.getdata())
bits = []
for r, g, b in pixels:
    bits.append(r & 1)
data = bytearray()
for i in range(0, len(bits), 8):
    byte_bits = bits[i:i+8]
    if len(byte_bits) < 8:
        break
    value = 0
    for bit in byte_bits:
        value = (value << 1) | bit
    data.append(value)
start = data.find(b"PK\x03\x04")
if start == -1:
    raise Exception("ZIP header tidak ditemukan")
data = data[start:]
eocd = data.rfind(b"PK\x05\x06")
if eocd == -1:
    raise Exception("EOCD ZIP tidak ditemukan")
comment_len = struct.unpack("<H", data[eocd + 20:eocd + 22])[0]
zip_end = eocd + 22 + comment_len
clean_zip = data[:zip_end]
with open("hidden_clean.zip", "wb") as f:
    f.write(clean_zip)
print("ZIP berhasil diekstrak ke hidden_clean.zip")
print("Ukuran ZIP:", len(clean_zip), "bytes")
```

lalu kita cek isi dari `hidden_clean.zip`

```
from zipfile import ZipFile

with ZipFile("hidden_clean.zip") as z:
    for info in z.infolist():
        print(info.filename, info.file_size)
```

output
```
flag.txt 26
```

Lalu kita extract

```
import pyzipper
password = b"SCTF_EXIF_S3CR3T"
with pyzipper.AESZipFile("hidden_clean.zip") as z:
    z.pwd = password
    z.extractall("out")
print(open("out/flag.txt").read())
```

output
```
SCTF26{m4try0shk4_lsb_z1p}
```

## Flag

```text
SCTF26{m4try0shk4_lsb_z1p}
```
