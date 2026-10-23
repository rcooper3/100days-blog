"""Freeze the Flask app into static files in build/, ready to upload to S3.

    python freeze.py            # build the site
    python freeze.py --serve    # build, then preview the frozen output on :8000
"""

import sys

from flask_frozen import Freezer

from app import app, get_posts

app.config.update(
    FREEZER_DESTINATION="build",
    FREEZER_REMOVE_EXTRA_FILES=True,   # drop pages for deleted posts
    FREEZER_IGNORE_404_NOT_FOUND=False,  # a broken internal link fails the build
)
freezer = Freezer(app)


@freezer.register_generator
def post():
    # Frozen-Flask also finds pages by following links, but listing them
    # explicitly means no post is missed even if nothing links to it.
    for p in get_posts():
        yield {"slug": p.slug}


@freezer.register_generator
def not_found_page():
    yield {}


if __name__ == "__main__":
    freezer.freeze()
    print(f"Built {len(get_posts())} posts into {app.config['FREEZER_DESTINATION']}/")
    if "--serve" in sys.argv:
        freezer.serve(port=8000)
