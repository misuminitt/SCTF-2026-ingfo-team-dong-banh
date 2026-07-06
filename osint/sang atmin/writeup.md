# Sang Atmin — Writeup

**Category    :** OSINT  
**Difficulty  :** Medium  
**hint 1      :** Instagram   
**hint 2      :** directory web "/"  
**Description :**

jika kamu sudah mendaftar SCTF26 pasti kamu kenal dengan sang atmin, bisakah kamu mengambil flag yg disembunyikan oleh atmin?
jangan lupa follow atmin yak heheh

## Solve

Pertama karna kita tau jika pembuat/probset chall dari event ini adalah `SteVenJr`, lalu kita coba langsung cari ke `Instagram` sesuai dari hint 1 dan ketemu akun nya `https://www.instagram.com/stevenjr_yt/`. Lalu pada bio akun instagramnya terdapat `https://cysec.darmajaya.ac.id/stevenjr/` ketika di akses hanya menampilkan website biasa, cuman karna pada hint 2 yaitu `directory web "/"` maka kita hanya berfokus pada directory web dan berfokus pada instagram, lalu ketika ku coba iseng mengakses /`flag.txt` ternyata itu berhasil dan memunculkan flagnya `https://cysec.darmajaya.ac.id/stevenjr/flag.txt`

## Flag

```text
SCTF26{0s1nt_k3_lf1_m4nt4p_c0y_S62df326}
```
