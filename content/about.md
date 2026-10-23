# About

I'm taking on the **#100DaysOfCode** challenge: an hour or so of coding every
day for 100 days, using Python.

I'm following Talk Python's
[#100DaysOfCode in Python](https://training.talkpython.fm/courses/explore_100days_in_python/100-days-of-code-in-python)
course, which splits the 100 days into 33 three-day modules. The first day of
each module is a video lesson, and the next two are hands-on practice.

This blog is my daily log of what I worked on, what I learned and what tripped
me up.

## How this site is built

Fittingly, it's built with Python. It's a small [Flask](https://flask.palletsprojects.com/)
app that turns one Markdown file per day into pages, and
[Frozen-Flask](https://frozen-flask.readthedocs.io/) turns it into static HTML
that's hosted on AWS S3 and CloudFront.
