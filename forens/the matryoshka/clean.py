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