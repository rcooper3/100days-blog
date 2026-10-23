# 100 Days of Python blog

Daily log for my #100DaysOfCode challenge, following Talk Python's
[#100DaysOfCode in Python](https://training.talkpython.fm/courses/explore_100days_in_python/100-days-of-code-in-python)
course. Live at **https://100days.cyberako.blog**.

The site is a small **Flask** app. **Frozen-Flask** turns it into static HTML,
which is hosted on S3 behind CloudFront. Nothing runs on a server, so the
hosting stays inside AWS's free allowances.

## Layout

| Path | What it is |
| --- | --- |
| `app.py` | The Flask app: routes for the home page, each day, About, the RSS feed and 404 |
| `posts.py` | Reads `content/posts/*.md`, parses the front matter, renders Markdown |
| `course.py` | The course's 33 modules, so each day is labelled with its topic and linked to the course materials |
| `freeze.py` | Freezes the app into `build/` |
| `new_post.py` | Creates the next day's post from a template |
| `templates/` | Jinja templates (`base.html` is the shared layout) |
| `static/` | CSS, favicon, and any images for posts (`static/images/...`) |
| `content/` | `about.md` and one Markdown file per day in `posts/` |
| `infra/template.yaml` | CloudFormation: private S3 bucket, CloudFront with OAC, security headers, an index.html rewrite function |
| `scripts/` | `request-cert.sh`, `deploy.sh`, `publish.sh`, `undeploy.sh` |

## Daily workflow

```bash
cd ~/Development/100days-blog
source .venv/bin/activate

python new_post.py                 # creates content/posts/day-NNN.md as a draft
flask --app app run --debug        # preview at http://127.0.0.1:5000 (drafts shown)

# edit the post, then set `draft: false` in its front matter
./scripts/publish.sh               # freeze, upload to S3, clear the CloudFront cache
```

`python freeze.py --serve` previews the frozen site exactly as it will be
published, at http://127.0.0.1:8000. Drafts are not included.

### Post format

```markdown
---
title: Building a pomodoro timer
day: 1
date: 2026-10-24
tags: datetime, timedelta
code: https://github.com/rcooper3/100Daysofcode/tree/main/days/01-03-datetimes
draft: false
---

The first paragraph becomes the summary on the home page and in the feed.

## What I learned
...
```

Only `title`, `day` and `date` are required. `code` adds a "my code" link,
and `summary` overrides the automatic one. Fenced code blocks
(```` ```python ````) are syntax-highlighted. Day 0 is the intro post and isn't
counted towards the 100.

## First-time setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
aws login
```

1. **Certificate.** Run `./scripts/request-cert.sh`. It requests an ACM certificate
   for `100days.cyberako.blog` in `us-east-1` (CloudFront only accepts
   certificates from there) and prints a validation CNAME.
2. **Validation CNAME in WordPress.com.** Go to Domains → cyberako.blog → DNS records
   and add the CNAME exactly as printed (Name like `_abc123.100days`, Value
   ending in `acm-validations.aws`). Re-run `request-cert.sh` until it says
   `ISSUED`, which usually takes 5–30 minutes.
3. **Deploy.** Run `CERTIFICATE_ARN=<arn from step 1> ./scripts/deploy.sh`. This
   creates the stack (CloudFront takes a few minutes), publishes the site, and
   prints the CloudFront hostname.
4. **Site CNAME in WordPress.com.** Add `100days` → `<something>.cloudfront.net`
   (the hostname printed in step 3).

After that, you only need `./scripts/publish.sh`. Run `deploy.sh` again only
if `infra/template.yaml` changes.

## Cost

Everything used is free at this size:

- **CloudFront**: the always-free tier covers 1 TB transfer and 10M requests per
  month. CloudFront Functions get 2M free invocations, and the first 1,000
  invalidation paths each month are free (`publish.sh` uses one).
- **ACM**: public certificates are free.
- **S3**: the site is well under 1 MB. Once the 12-month free tier has expired,
  storage and uploads come to a fraction of a cent per month.
- **DNS** stays in WordPress.com, so there's no Route 53 hosted zone ($0.50/month).

## Teardown

`./scripts/undeploy.sh` empties the bucket, deletes the stack, and offers to delete
the certificate. Your posts in `content/` are untouched. Remove the two
WordPress.com CNAMEs by hand if you're finished for good.
