import subprocess

MSG_DELIMITER = b"\xFF"


class Djot:
    """
    Poor man's IPC via stdin/stdout pipes:
    Python sends djot content to nodejs subprocess, gets back html content.

    Usage:
        djot = Djot()
        html = djot.to_html('_and the pirate on the boat_')

    Each message terminates with a 0xFF byte.
    Because this byte does not appear in valid UTF-8, it's a safe delimiter.
    """

    def __init__(self):
        self.proc = subprocess.Popen(
            ["node", "src/bloghead/djot-server.dist.js"],  # TODO don't hardcode js path
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            bufsize=0,  # avoids blocking proc.stdout.read(n)
        )
        self.buffer = b""

    def __del__(self):
        self.proc.kill()

    def to_html(self, src: str):
        # Write to nodejs proc:
        self.proc.stdin.write(src.encode())
        self.proc.stdin.write(MSG_DELIMITER)
        self.proc.stdin.flush()

        # Read response from it:
        while (end_index := self.buffer.find(MSG_DELIMITER)) == -1:
            self.buffer += self.proc.stdout.read(4096)
        resp = self.buffer[:end_index]
        self.buffer = self.buffer[end_index + 1 :]
        return resp.decode()


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
