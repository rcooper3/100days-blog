"""The Talk Python #100DaysOfCode course outline, used to label each day's post.

Each module covers three days: day one is the video lesson, days two and
three are hands-on practice. Folder names match `days/` in the course repo.
"""

COURSE_REPO = "https://github.com/talkpython/100daysofcode-with-python-course/tree/master/days"

MODULES = [
    (1, 3, "01-03-datetimes", "Datetimes"),
    (4, 6, "04-06-collections", "Collections module"),
    (7, 9, "07-09-data-structures", "Data structures"),
    (10, 12, "10-12-pytest", "Testing with pytest"),
    (13, 15, "13-15-text-games", "Text-based games and classes"),
    (16, 18, "16-18-listcomprehensions-generators", "List comprehensions and generators"),
    (19, 21, "19-21-itertools", "Itertools"),
    (22, 24, "22-24-decorators", "Decorators"),
    (25, 27, "25-27-error-handling", "Error handling"),
    (28, 30, "28-30-regex", "Regular expressions"),
    (31, 33, "31-33-logging", "Logging"),
    (34, 36, "34-36-refactoring", "Refactoring and Pythonic code"),
    (37, 39, "37-39-csv-data-analysis", "CSV data analysis"),
    (40, 42, "40-42-json-data", "JSON data"),
    (43, 45, "43-45-search-api", "Consuming HTTP services"),
    (46, 48, "46-48-beautifulsoup4", "Web scraping with BeautifulSoup4"),
    (49, 51, "49-51-measuring-perf", "Measuring performance"),
    (52, 54, "52-54-feedparser", "RSS feeds with feedparser"),
    (55, 57, "55-57-uplink", "Structured APIs with Uplink"),
    (58, 60, "58-60-twitter-api", "Twitter API"),
    (61, 63, "61-63-github-api", "GitHub API"),
    (64, 66, "64-66-email-smtplib", "Sending email with smtplib"),
    (67, 69, "67-69-pyperclip", "Clipboard automation with pyperclip"),
    (70, 72, "70-72-openpyxl-excel-automation", "Excel automation with openpyxl"),
    (73, 75, "73-75-selenium", "Web automation with Selenium"),
    (76, 78, "76-78-flask", "Web apps with Flask"),
    (79, 81, "79-81-sqlite3", "Databases with sqlite3"),
    (82, 84, "82-84-dataviz-plotly", "Data visualisation with Plotly"),
    (85, 87, "85-87-full-stack-easy", "Full-stack web apps made easy"),
    (88, 90, "88-90-home-inventory-app", "Home inventory app"),
    (91, 93, "91-93-sqlalchemy", "Databases with SQLAlchemy"),
    (94, 96, "94-96-guis", "Python GUIs"),
    (97, 99, "97-99-online-game-api", "Online game API with Flask"),
    (100, 100, "100-freestyle", "Freestyle"),
]


def module_for_day(day):
    """Return (folder, title, day_within_module) for a day number, or None."""
    for start, end, folder, title in MODULES:
        if start <= day <= end:
            return folder, title, day - start + 1
    return None


def module_url(folder):
    return f"{COURSE_REPO}/{folder}"
