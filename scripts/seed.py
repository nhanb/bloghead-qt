#!/usr/bin/env python
from pathlib import Path
from sys import argv

from bloghead.persistence import Blog

fpath = Path(argv[1]) if len(argv) == 2 else Path("Site1.bloghead")

if fpath.is_file():
    confirmation = input("File exists. Replace? (y/N) ")
    if confirmation.lower() != "y":
        print("Aborted")
        exit(1)

    fpath.unlink()
    print("Removed existing file:", fpath)

blog = Blog(fpath).init_schema()

seeds = sorted(Path("scripts/seed-data").glob("*.seed"))
for seed in seeds:
    slug = seed.name.split(".")[1]
    with open(seed, "r") as sf:
        draft, article_type, title, content = sf.read().strip().split("\n", maxsplit=3)
    blog.create_article(
        slug=slug,
        title=title,
        content=content,
        is_draft=(draft == "draft"),
        is_page=(article_type == "page"),
    )
print("Created", len(seeds), "articles.")
