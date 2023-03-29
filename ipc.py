# Playground code. Mostly outdated.

import os
import socket
import sys

if len(sys.argv) != 2 or (command := sys.argv[1]) not in {"server", "client"}:
    print("Usage: python ipy.py server|client")
    exit(1)

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
SOCK_ADDR = "bloghead.sock"
HEADER_SIZE = 4


def server():
    os.unlink(SOCK_ADDR)
    sock.bind(SOCK_ADDR)
    sock.listen(1)
    conn, _ = sock.accept()

    leftover = b""
    while True:
        should_continue, leftover = handle_message(conn, leftover)
        if not should_continue:
            break


def handle_message(conn, leftover: bytes):
    header = leftover
    body = b""

    # Header loop
    while True:
        if len(header) >= HEADER_SIZE:
            body = header[HEADER_SIZE:]
            header = header[:HEADER_SIZE]
            break

        chunk = conn.recv(HEADER_SIZE)
        if not chunk:
            print("header: not enough data")
            return False, None

        print("header chunk:", chunk)
        header += chunk

    body_size = int.from_bytes(header, "little", signed=False)
    print("Body size:", body_size)

    # Body loop
    bufsize = min(4096, body_size)
    leftover = b""
    while True:
        chunk = conn.recv(bufsize)

        if not chunk:
            print("body: connection closed")
            return False, None

        print("body chunk:", chunk)
        body += chunk

        if len(body) >= body_size:
            leftover = body[body_size:]
            body = body[:body_size]
            break

    process_body(conn, body)
    return True, leftover


def process_body(conn, body: bytes):
    body = b"processed " + body
    size = len(body).to_bytes(HEADER_SIZE, "little", signed=False)
    conn.sendall(size + body)


def client():
    print("Running client")
    sock.connect(SOCK_ADDR)

    while True:
        body = input("Enter msg: ").encode()
        size = len(body).to_bytes(HEADER_SIZE, "little", signed=False)
        sock.sendall(size + body)


globals()[command]()
