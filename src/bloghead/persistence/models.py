import datetime

import peewee as pw

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%SZ"
DATABASE = pw.SqliteDatabase(None)


class Article(pw.Model):
    slug = pw.CharField()
    title = pw.CharField()
    content = pw.TextField()
    is_page = pw.BooleanField(default=False)
    is_draft = pw.BooleanField(default=True)
    created_at = pw.DateTimeField(
        default=datetime.datetime.now,
        formats=[DATETIME_FORMAT],
    )

    class Meta:
        database = DATABASE


TABLES = [Article]


# The following are Views, not Tables


class Post(Article):
    class Meta:
        db_table = "post"


class Page(Article):
    class Meta:
        db_table = "page"
