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
