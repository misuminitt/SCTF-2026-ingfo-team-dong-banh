from Crypto.Util.number import long_to_bytes
from math import isqrt


N = 123436627937364220533270481649818241453723967384115317594580901509579002824492262533794630377279193802667379328735965163616334782488239489087324009223510505963533224573946190880685234990343308688615124347997748068891941544581957313716048480814498261130855640228654079732420165464995937087159234466591205031751

e = 52286779493719729111591951649018041120591431350255885880577954404417007096031542111805947925585000343367614092261219489270418623551496489397138684909838323937877627127780914093840297043462429076058522270894279052896963585381556897521605273988530094327726762243365869008195095849872139679930482993327784210855

C = 18307439754530257973400778807902998716623475594653775301290303045002722390993302047608662285458447774397358610645344936545249766330424835416841280732941976558802246418405394883748778049855176308710527927843514145576183854220758621096505224039138515443926112102198919593418899324370114428727718628785880647777


def continued_fraction(n, d):
    result = []

    while d:
        a = n // d
        result.append(a)
        n, d = d, n - a * d

    return result


def convergents(cf):
    n0, n1 = 0, 1
    d0, d1 = 1, 0

    for a in cf:
        n2 = a * n1 + n0
        d2 = a * d1 + d0

        yield n2, d2

        n0, n1 = n1, n2
        d0, d1 = d1, d2


def is_perfect_square(x):
    if x < 0:
        return False

    r = isqrt(x)
    return r * r == x


def recover_d():
    cf = continued_fraction(e, N)

    for k, d in convergents(cf):
        if k == 0:
            continue

        if (e * d - 1) % k != 0:
            continue

        phi = (e * d - 1) // k

        s = N - phi + 1
        discr = s * s - 4 * N

        if not is_perfect_square(discr):
            continue

        t = isqrt(discr)

        if (s + t) % 2 != 0:
            continue

        p = (s + t) // 2
        q = (s - t) // 2

        if p * q == N:
            return d

    return None


d = recover_d()

if d is None:
    d = int(
        "1c7dfaeaeefcc88dc4a77870301126e1176f9ccc37aaebca832e0bb03ae628f269f",
        16
    )

print("[+] d =", hex(d))

m = pow(C, d, N)
flag = long_to_bytes(m)

print("[+] flag:", flag.decode())