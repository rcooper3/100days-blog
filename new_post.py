"""Start today's post: python new_post.py [day]

Without a day number it picks the day after the latest post. The file is
created as a draft; set `draft: false` when you're ready to publish.
"""

import sys
from datetime import date

from course import module_for_day
from posts import POSTS_DIR, load_posts

TEMPLATE = """---
title: {title}
day: {day}
date: {today}
tags: {tags}
code:
draft: true
---

{intro}

## What I did

-

## What I learned

-

## Code

```python

```

## Tomorrow

-
"""


def main():
    if len(sys.argv) > 1:
        day = int(sys.argv[1])
    else:
        posts = load_posts(include_drafts=True)
        day = max((p.day for p in posts), default=0) + 1

    path = POSTS_DIR / f"day-{day:03d}.md"
    if path.exists():
        sys.exit(f"{path} already exists")

    module = module_for_day(day)
    if module:
        folder, topic, nth = module
        title = topic
        tags = topic.lower()
        intro = f"Day {nth} of the *{topic}* module."
    else:
        title, tags, intro = "Untitled", "", ""

    path.write_text(TEMPLATE.format(title=title, day=day, today=date.today().isoformat(), tags=tags, intro=intro), encoding="utf-8")
    print(f"Created {path}")


if __name__ == "__main__":
    main()
