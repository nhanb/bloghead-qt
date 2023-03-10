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
            "create view post as select * from article where is_page = false;",
        )
        self.db.execute_sql(
            "create view page as select * from article where is_page = true;",
        )
        return self

    def create_article(self, **kwargs) -> int:
        article = Article(**kwargs)
        article.save()
        return article.id

    def count_pages(self) -> int:
        return Page.select().count()

    def count_posts(self) -> int:
        return Post.select().count()

    def get_page_title(self, index: int) -> tuple[int, str]:
        """Returns tuple(id, title)"""
        page = Page.select(Page.id, Page.title).order_by(Page.created_at.desc())[index]
        return (page.id, page.title)

    def get_post_title(self, index: int) -> tuple[int, str]:
        """Returns tuple(id, title)"""
        post = Post.select(Post.id, Post.title).order_by(Post.created_at.desc())[index]
        return (post.id, post.title)
