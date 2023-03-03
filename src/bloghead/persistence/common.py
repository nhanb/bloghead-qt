import sqlite3
from importlib.resources import read_binary
from pathlib import Path

from dataclass import dataclass


@dataclass(slots=True)
class Blog:
    """
    Provides read/write access to a blog's underlying files on disk.
    DO NOT initialize a Blog() directly. Use new_blog() or open_blog() instead.
    """

    conn: sqlite3.Connection
    path: Path
    attachments_path: Path

    def __init__(self, path: Path):
        self.conn = sqlite3.connect(path / "data.bloghead")
        self.path = path
        self.attachments_path = path / "attachments"


def new_blog(path: Path) -> Blog:
    # Create necessary folders and file
    path.mkdir(parents=True)
    blog = Blog(path)
    blog.attachments_path.mkdir()

    # Initialize db schema
    schema_sql = read_binary("bloghead", "persistence.schema.sql")
    blog.conn.cursor().executescript(schema_sql)

    return blog


def open_blog(path: Path) -> Blog:
    return Blog(path)
