import re
import sqlite3
from dataclasses import dataclass
from importlib import resources
from pathlib import Path


def regexp(expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None


@dataclass(slots=True)
class Blog:
    """
    Provides read/write access to a blog's underlying file on disk.
    To open: `blog = Blog(path)`
    To create new: `blog = Blog(path).init_schema()`
    """

    conn: sqlite3.Connection
    path: Path

    def __init__(self, path: Path):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.conn.create_function("REGEXP", 2, regexp)

    def init_schema(self):
        schema_sql = resources.read_text("bloghead.persistence", "schema.sql")
        self.conn.cursor().executescript(schema_sql)
        return self
