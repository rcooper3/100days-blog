"""The #100DaysOfCode blog as a Flask app.

Run it locally while writing (pages reload as you edit posts):

    flask --app app run --debug

Publish by freezing it to static HTML (see freeze.py), which is what gets
uploaded to S3 and served by CloudFront.
"""

from email.utils import format_datetime
from datetime import datetime, time, timezone
from pathlib import Path

from flask import Flask, Response, abort, render_template
from pygments.formatters import HtmlFormatter

from posts import load_posts, render_markdown

SITE = {
    "title": "100 Days of Python",
    "description": "Daily notes from my #100DaysOfCode challenge, following the Talk Python course.",
    "url": "https://100days.cyberako.blog",
    "author": "Rob",
    "total_days": 100,
}

ABOUT_FILE = Path(__file__).parent / "content" / "about.md"

app = Flask(__name__)


def get_posts():
    # Drafts show up when running `flask run --debug`, never in the published site.
    return load_posts(include_drafts=app.debug)


@app.context_processor
def inject_site():
    return {"site": SITE}


@app.template_filter("nice_date")
def nice_date(value):
    return value.strftime("%a %-d %b %Y")


@app.template_filter("rfc822")
def rfc822(value):
    """The date format RSS readers expect, e.g. 'Sat, 24 Oct 2026 12:00:00 +0000'."""
    return format_datetime(datetime.combine(value, time(12), tzinfo=timezone.utc))


@app.route("/")
def index():
    posts = get_posts()
    by_day = {p.day: p for p in posts}
    grid = [(day, by_day.get(day)) for day in range(1, SITE["total_days"] + 1)]
    done = sum(1 for p in posts if p.day >= 1)
    return render_template("index.html", posts=posts, grid=grid, done=done)


@app.route("/days/<slug>/")
def post(slug):
    posts = get_posts()  # newest first
    for i, p in enumerate(posts):
        if p.slug == slug:
            newer = posts[i - 1] if i > 0 else None
            older = posts[i + 1] if i + 1 < len(posts) else None
            return render_template("post.html", post=p, newer=newer, older=older)
    abort(404)


@app.route("/about/")
def about():
    return render_template("about.html", body_html=render_markdown(ABOUT_FILE.read_text(encoding="utf-8")))


@app.route("/feed.xml")
def feed():
    xml = render_template("feed.xml", posts=get_posts()[:20])
    return Response(xml, mimetype="application/xml")


@app.route("/pygments.css")
def pygments_css():
    """Syntax-highlighting colours for code blocks, light and dark."""
    light = HtmlFormatter(style="default").get_style_defs(".highlight")
    dark = HtmlFormatter(style="github-dark").get_style_defs(".highlight")
    css = f"{light}\n@media (prefers-color-scheme: dark) {{\n{dark}\n}}\n"
    return Response(css, mimetype="text/css")


# CloudFront serves this page for any missing URL (see infra/template.yaml).
@app.route("/404.html")
def not_found_page():
    return render_template("404.html")


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404
