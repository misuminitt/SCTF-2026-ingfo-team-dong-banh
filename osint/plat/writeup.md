# Plat — Writeup

**Category    :** OSINT  
**Difficulty  :** Medium  
**File        :** ![mobil](mobil.png)
**Description :**

ini mobil siapa bro? coba cariin si ini mobil punya siapa

Format flag: SCTF26{username_instagram_jenis_mobil_platmobil}
note: username instagram kecil semua, jenis mobil huruf pertama kapital dan plat huruf kapital
Example: SCTF26{stevenjr_yt_Honda_HRV_Class_BE2230AGY}

## Solve

Kita mulai coba cari dengan masukan plat nomornya `B1673SS0` ke search engine google, maka akan tampil postingan instagram dari `raffinagita1717` `https://www.instagram.com/p/CLis8CTMI7D/`

![rafi](image.png)

Jika kita lihat plat nomor pada mobil di postingan itu sama dengan gambar pada soal yaitu `B1673SSO`, lalu untuk type mobil nya adalah `Mercedes Benz V Class`

## Flag

```text
SCTF26{raffinagita1717_Mercedes_Benz_V_Class_B1673SSO}
```
