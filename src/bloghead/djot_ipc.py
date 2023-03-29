import socket
import subprocess

HEADER_SIZE = 4
ENDIANNESS = "little"
SIGNED = False


class Djot:
    """
    Poor man's IPC via stdin/stdout pipes:
    Python sends djot content to nodejs subprocess, gets back html content.

    Usage:
        djot = Djot()
        html = djot.to_html('_and the pirate on the boat_')

    Here I'm implementing a simple message boundary protocol:
    Each message starts with a 4-byte integer (little endian, unsigned) header
    which is the length (in bytes) of said message.
    """

    def __init__(self):
        self.proc = subprocess.Popen(
            ["node", "src/djot.server.js"],  # TODO don't hardcode js path
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        self._leftover = b""

    def __del__(self):
        self.proc.kill()

    def to_html(self, src: str):
        self._write(src)
        return self._read()

    def _write(self, body: str):
        header = len(body).to_bytes(HEADER_SIZE, ENDIANNESS, signed=SIGNED)
        self.proc.stdin.write(header + body.encode())
        self.proc.stdin.flush()

    def _read(self) -> str:
        header = self._leftover
        body = b""

        # Header loop
        while True:
            if len(header) >= HEADER_SIZE:
                body = header[HEADER_SIZE:]
                header = header[:HEADER_SIZE]
                break

            chunk = self.proc.stdout.read(HEADER_SIZE)
            if not chunk:
                raise Exception("header: not enough data")

            print("header chunk:", chunk)
            header += chunk

        body_size = int.from_bytes(header, ENDIANNESS, signed=SIGNED)
        print("Body size:", body_size)

        # Body loop
        bufsize = min(4096, body_size)
        self._leftover = b""
        while True:
            if len(body) >= body_size:
                self._leftover = body[body_size:]
                body = body[:body_size]
                break

            chunk = self.proc.stdout.read(bufsize)
            if not chunk:
                raise Exception("body: connection closed")

            print("body chunk:", chunk)
            body += chunk

        return body.decode()


if __name__ == "__main__":
    djot = Djot()
    msg = """
# Hi.

My _first_ name *is*:

```html
heh
```
    """
    print("Sending:", msg)
    resp = djot.to_html(msg)
    print("Got:", resp)
