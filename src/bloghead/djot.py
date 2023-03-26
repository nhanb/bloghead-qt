import subprocess


def to_html(src: str) -> str:
    cmd = subprocess.run(["djot"], input=src.encode(), capture_output=True, check=True)
    return cmd.stdout.decode()
