# Silent Exfiltration — Writeup

**Category    :** Forensics  
**Difficulty  :** Medium  
**File        :** silent_exfil.pcap   
**Description :**

We noticed strange network traffic. Find out what was stolen.

## Solve

Dari deskripsi challenge sudah jelas kalau fokusnya ada di trafik jaringan, jadi langkah pertama adalah identifikasi isi file `pcap`. Aku mulai dengan cek metadata file dan protokol apa saja yang muncul

```bash
file silent_exfil.pcap
capinfos silent_exfil.pcap
tshark -r silent_exfil.pcap -q -z io,phs
```

Output pentingnya menunjukkan kalau capture ini sangat kecil dan seluruh paketnya hanya berisi `DNS` di atas `UDP`

```text
silent_exfil.pcap: pcap capture file, microsecond ts (little-endian) - version 2.4 (Raw IPv4, capture length 65535)
```

```text
Number of packets:   14
Capture duration:    0.008334 seconds
```

```text
frame                                    frames:14 bytes:901
  raw                                    frames:14 bytes:901
    ip                                   frames:14 bytes:901
      udp                                frames:14 bytes:901
        dns                              frames:14 bytes:901
```

Karena cuma ada DNS, kemungkinan besar eksfiltrasi dilakukan lewat query name. Jadi aku dump field DNS untuk lihat domain apa saja yang ditanyakan

```bash
tshark -r silent_exfil.pcap -T fields -e frame.number -e ip.src -e ip.dst -e dns.flags.response -e dns.qry.name
```

Output-nya seperti ini

```text
1   192.168.1.100   8.8.8.8   False   KNBVIRRSGZ.update.sctf.my.id
2   192.168.1.100   8.8.8.8   False   google.com
3   192.168.1.100   8.8.8.8   False   5WI3TTL4ZX.update.sctf.my.id
4   192.168.1.100   8.8.8.8   False   google.com
5   192.168.1.100   8.8.8.8   False   QZRRNR2HEN.update.sctf.my.id
6   192.168.1.100   8.8.8.8   False   google.com
7   192.168.1.100   8.8.8.8   False   DUGEYG4X3Q.update.sctf.my.id
8   192.168.1.100   8.8.8.8   False   google.com
9   192.168.1.100   8.8.8.8   False   MNQXAXZUNY.update.sctf.my.id
10  192.168.1.100   8.8.8.8   False   google.com
11  192.168.1.100   8.8.8.8   False   2GY6JVGE2X.update.sctf.my.id
12  192.168.1.100   8.8.8.8   False   google.com
13  192.168.1.100   8.8.8.8   False   2.update.sctf.my.id
14  192.168.1.100   8.8.8.8   False   google.com
```

Terlihat ada pola query ke `*.update.sctf.my.id` yang diselingi query `google.com` sebagai kamuflase. Label subdomain seperti `KNBVIRRSGZ`, `5WI3TTL4ZX`, dan seterusnya terlihat seperti karakter `Base32`, jadi aku gabungkan semua label mencurigakan lalu decode

solve.py
```python
from __future__ import annotations

import base64
import subprocess
from pathlib import Path

PCAP_PATH = Path('silent_exfil.pcap')
TARGET_SUFFIX = '.update.sctf.my.id'


def extract_labels_from_pcap(pcap_path: Path) -> list[str]:
    command = [
        'tshark',
        '-r',
        str(pcap_path),
        '-T',
        'fields',
        '-e',
        'dns.qry.name',
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=True)

    labels: list[str] = []
    for query_name in result.stdout.splitlines():
        if not query_name.endswith(TARGET_SUFFIX):
            continue

        label = query_name[: -len(TARGET_SUFFIX)]
        if label:
            labels.append(label)

    return labels


def decode_flag(labels: list[str]) -> str:
    encoded = ''.join(labels)
    padding = '=' * ((8 - len(encoded) % 8) % 8)
    decoded = base64.b32decode(encoded + padding, casefold=True)
    return decoded.decode()


def main() -> None:
    labels = extract_labels_from_pcap(PCAP_PATH)
    print('[+] Label DNS mencurigakan:')
    for label in labels:
        print(f'    - {label}')

    flag = decode_flag(labels)
    print(f'\n[+] Flag: {flag}')


if __name__ == '__main__':
    main()
```

Output nya akan mengumpulkan semua label mencurigakan lalu mendecode hasil eksfiltrasinya

```text
[+] Label DNS mencurigakan:
    - KNBVIRRSGZ
    - 5WI3TTL4ZX
    - QZRRNR2HEN
    - DUGEYG4X3Q
    - MNQXAXZUNY
    - 2GY6JVGE2X
    - 2

[+] Flag: SCTF26{dns_3xf1ltr4t10n_pcap_4n4ly515}
```

## Flag

```text
SCTF26{dns_3xf1ltr4t10n_pcap_4n4ly515}
```
