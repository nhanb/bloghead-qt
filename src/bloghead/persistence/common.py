from dataclasses import dataclass
from pathlib import Path

import peewee

from . import models
from .models import Article, Page, Post


@dataclass(slots=True)
class Blog:
    """
    Provides read/write access to a blog's underlying file on disk.
    To open: `blog = Blog(path)`
    To create new: `blog = Blog(path).init_schema()`
    """

    db: peewee.SqliteDatabase
    path: Path

    def __init__(self, path: Path):
        self.path = path
        self.db = models.DATABASE
        self.db.init(str(path))
        self.db.connect()

    def init_schema(self):
        self.db.create_tables(models.TABLES)
        self.db.execute_sql(
            "create view post as select * from article where is_page = false order by id desc;",
        )
        self.db.execute_sql(
            "create view page as select * from article where is_page = true order by id desc;",
        )
        return self

    def create_article(self, **kwargs) -> int:
        return Article.insert(**kwargs).execute()

    def count_pages(self) -> int:
        return Page.select().count()

    def count_posts(self) -> int:
        return Post.select().count()

    def get_page_title(self, index: int) -> tuple[int, str]:
        """Returns tuple(id, title)"""
        page = Page.select(Page.id, Page.title)[index]
        return (page.id, page.title)

    def get_post_title(self, index: int) -> tuple[int, str]:
        """Returns tuple(id, title)"""
        post = Post.select(Post.id, Post.title)[index]
        return (post.id, post.title)

    def get_article(self, id: int) -> Article:
        return Article.get(Article.id == id)
