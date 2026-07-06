# atmin suka naik gunung — Writeup

**Category    :** OSINT  
**Difficulty  :** Medium  
**File        :** ![gunung](gunung.jpg)
**Description :**

si atmin ini lagi suka sukanya naik gunung, cuma dia ini ga mau naik gunung yg beneran
bisa ga cari nama gunungnya apa?

Format Flag: SCTF26{Nama_Gunung_Nama_Developer} huruf pertama kapital

## Solve

Pada format flag di deskripsi soal tertulis nama_developer yang berarti sudah pasti gunung pada game `Roblox`, asumsi nya juga diperkuat karna pada gambar memiliki grafik yang khas dengan game `Roblox`. Jika kita masukan gambar nya ke `Google Lens` maka akan muncul postingan dari `X` yaitu `https://x.com/roblox_fess/status/1943001366114287711`

![x](image.png)

Dipostingan tersebut tertulis jelas jika si pembuat postingan bermain di `map gunung talamau`, jika kita cari `Gunung Talamau` atau `Mount Talamau` pada game Roblox maka akan muncul sang developernya yaitu `Imaginature Studio`

![roblox](image-1.png)

## Flag

```text
SCTF26{Gunung_Talamau_Imaginature_Studio}
```
