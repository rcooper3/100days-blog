"""Load the daily posts from content/posts/*.md.

Each post is a Markdown file with a small front-matter header:

    ---
    title: My first pomodoro timer
    day: 1
    date: 2026-10-24
    tags: datetime, timedelta
    code: https://github.com/rcooper3/100Daysofcode/tree/main/days/01-03-datetimes
    draft: false
    ---

    The post body in Markdown...

Only `title`, `day` and `date` are required.
"""

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import markdown

from course import module_for_day, module_url

POSTS_DIR = Path(__file__).parent / "content" / "posts"
FRONT_MATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", re.DOTALL)


@dataclass
class Post:
    title: str
    day: int
    date: date
    body_html: str
    summary: str
    tags: list = field(default_factory=list)
    code: str = ""
    draft: bool = False
    source: Path = None

    @property
    def slug(self):
        return f"{self.day:03d}"

    @property
    def module(self):
        """(folder, title, day_within_module) from the course outline, if any."""
        return module_for_day(self.day)

    @property
    def course_url(self):
        return module_url(self.module[0]) if self.module else ""


def parse_front_matter(text, path):
    match = FRONT_MATTER.match(text)
    if not match:
        raise ValueError(f"{path.name}: missing '---' front matter block")
    header, body = match.groups()
    meta = {}
    for line in header.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if not sep:
            raise ValueError(f"{path.name}: bad front matter line {line!r}")
        meta[key.strip().lower()] = value.strip()
    return meta, body


def summarise(html, length=200):
    """Plain-text version of the first paragraph, for the index and the feed."""
    match = re.search(r"<p>(.*?)</p>", html, re.DOTALL)
    text = re.sub(r"<[^>]+>", "", match.group(1)) if match else ""
    text = " ".join(text.split())
    if len(text) > length:
        text = text[:length].rsplit(" ", 1)[0] + "…"
    return text


def render_markdown(text):
    return markdown.markdown(
        text,
        extensions=["fenced_code", "codehilite", "tables", "sane_lists"],
        extension_configs={"codehilite": {"css_class": "highlight", "guess_lang": False}},
    )


def load_post(path):
    meta, body = parse_front_matter(path.read_text(encoding="utf-8"), path)
    for required in ("title", "day", "date"):
        if not meta.get(required):
            raise ValueError(f"{path.name}: front matter needs '{required}'")

    day = int(meta["day"])
    if not 0 <= day <= 100:
        raise ValueError(f"{path.name}: day must be between 0 and 100, got {day}")

    body_html = render_markdown(body)
    return Post(
        title=meta["title"],
        day=day,
        date=date.fromisoformat(meta["date"]),
        body_html=body_html,
        summary=meta.get("summary") or summarise(body_html),
        tags=[t.strip() for t in meta.get("tags", "").split(",") if t.strip()],
        code=meta.get("code", ""),
        draft=meta.get("draft", "false").lower() in ("true", "yes", "1"),
        source=path,
    )


def load_posts(include_drafts=False):
    """All posts, newest day first. Raises if two posts claim the same day."""
    posts = [load_post(p) for p in sorted(POSTS_DIR.glob("*.md"))]
    if not include_drafts:
        posts = [p for p in posts if not p.draft]

    seen = {}
    for post in posts:
        if post.day in seen:
            raise ValueError(f"Day {post.day} is used by both {seen[post.day].name} and {post.source.name}")
        seen[post.day] = post.source

    return sorted(posts, key=lambda p: p.day, reverse=True)
