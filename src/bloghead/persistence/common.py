import re
import sqlite3
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path


def regexp(expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


@dataclass(slots=True)
class Article:
    id: int
    slug: str
    title: str
    content: str


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
        self.conn.row_factory = dict_factory
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.conn.execute("PRAGMA busy_timeout = 4000;")

    def init_schema(self):
        sql = files("bloghead.persistence").joinpath("schema.sql").read_text()
        self.conn.cursor().executescript(sql)
        return self

    def _execute(self, query, params=None):
        params = params or []
        with self.conn:
            self.conn.execute(query, params)

    def _fetch_one(self, query, params=None):
        params = params or []
        with self.conn:
            cur = self.conn.execute(query, params)
            return cur.fetchone()

    def _fetch_all(self, query, params=None):
        params = params or []
        with self.conn:
            cur = self.conn.execute(query, params)
            return cur.fetchall()

    def create_article(self, **kwargs) -> int:
        """
        Returns article's id
        """
        columns = ",".join(kwargs.keys())
        placeholders = ",".join("?" for _ in range(len(kwargs)))
        query = f"insert into article({columns}) values({placeholders}) returning id;"
        params = [val for val in kwargs.values()]
        return self._fetch_one(query, params)["id"]

    def get_article(self, id: int) -> Article:
        row = self._fetch_one(
            "select id, slug, title, content from article where id=?;",
            [id],
        )
        return Article(**row)

    def list_pages(self) -> list[tuple[int, str]]:
        rows = self._fetch_all("select id, title from page;")
        return [(row["id"], row["title"]) for row in rows]

    def list_posts(self) -> list[tuple[int, str]]:
        rows = self._fetch_all("select id, title from post;")
        return [(row["id"], row["title"]) for row in rows]

    def save_article(self, id, *, title, slug, content):
        self._execute(
            "update article set title=?, slug=?, content=? where id=?;",
            [title, slug, content, id],
        )
