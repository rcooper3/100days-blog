"""Start today's post: python new_post.py [day]

Without a day number it picks the day after the latest post. The file is
created as a draft; set `draft: false` when you're ready to publish.

If the code repo is checked out next to this one (../100days-python), it also
creates the module's folder there and links the post to it.
"""

import sys
from datetime import date
from pathlib import Path

from course import MODULES, module_for_day, module_url
from posts import POSTS_DIR, load_posts

CODE_REPO_DIR = Path(__file__).parent.parent / "100days-python"
CODE_REPO_URL = "https://github.com/rcooper3/100days-python/tree/main/days"

TEMPLATE = """---
title: {title}
day: {day}
date: {today}
tags: {tags}
code: {code}
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


def ensure_code_folder(folder, topic):
    """Create days/<folder>/ in the code repo with a README, if not there yet.

    Returns the folder's GitHub URL, or "" if the code repo isn't checked out.
    """
    if not CODE_REPO_DIR.is_dir():
        return ""
    module_dir = CODE_REPO_DIR / "days" / folder
    if not module_dir.exists():
        start, end = next((s, e) for s, e, f, _ in MODULES if f == folder)
        days = f"day {start}" if start == end else f"days {start}-{end}"
        module_dir.mkdir(parents=True)
        (module_dir / "README.md").write_text(
            f"# {topic} ({days})\n\n"
            f"- Course materials: {module_url(folder)}\n"
            f"- Blog: https://100days.cyberako.blog/days/{start:03d}/\n",
            encoding="utf-8",
        )
        print(f"Created {module_dir}")
    return f"{CODE_REPO_URL}/{folder}"


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
        code = ensure_code_folder(folder, topic)
    else:
        title, tags, intro, code = "Untitled", "", "", ""

    path.write_text(TEMPLATE.format(title=title, day=day, today=date.today().isoformat(), tags=tags, intro=intro, code=code), encoding="utf-8")
    print(f"Created {path}")


if __name__ == "__main__":
    main()
