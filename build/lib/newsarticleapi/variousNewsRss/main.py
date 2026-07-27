import argparse
import csv
import datetime
import json
import os

import feedparser
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
}

# anchor paths to this file so the tool works no matter which cwd it's launched from
BASE_DIR = os.path.dirname(__file__)
CSV_PATH = os.path.join(BASE_DIR, "rsss.csv")
folderpath = os.path.join(BASE_DIR, "..", "..", "newsposts")

oneDayAgo = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)


def getListofRssLinks(filePath: str) -> list[tuple[str, ...]]:
    # each CSV row is: url, tag1, tag2, ...  ->  (url, tag1, tag2, ...)
    urlAndTags = []
    with open(filePath, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            urlAndTags.append(tuple(ele.strip() for ele in row))

    return urlAndTags


def _extractText(entry) -> str:

    rawHTML = entry.get("content", [{}])[0].get("value")
    if rawHTML is None:
        rawHTML = entry.get("summary", "")
    return BeautifulSoup(rawHTML, "html.parser").get_text(separator="\n").strip()


# Takes one feed URL plus its tags, returns its entries in the readme JSON shape.
# cutoff, when given, keeps only entries published strictly after it.
def getFullResponseFromFeed(feedUrl: str, tags: list[str], cutoff: datetime.datetime | None = None) -> list[dict]:
    jsonResponse = []
    rss = feedparser.parse(feedUrl, agent=HEADERS["User-Agent"])

    if rss.bozo and not rss.entries:
        print("feed failure: " + feedUrl + " : " + str(rss.get("status")) + " : " + str(rss.get("bozo_exception")))
        return jsonResponse

    # a naive cutoff is assumed to be UTC so it compares cleanly with feed dates
    if cutoff is not None and cutoff.tzinfo is None:
        cutoff = cutoff.replace(tzinfo=datetime.timezone.utc)

    for entry in rss.entries:
        # feedparser gives published_parsed as a UTC struct_time, or None when undated
        publishedStruct = entry.get("published_parsed")
        publishedDate = (
            datetime.datetime(*publishedStruct[:6], tzinfo=datetime.timezone.utc)
            if publishedStruct else None
        )

        # skip dated entries at/before the cutoff; undated entries have no date to
        # test against, so they're always kept (matches the substack scraper)
        if cutoff is not None and publishedDate is not None and publishedDate <= cutoff:
            continue

        jsonResponse.append({
            "title": entry.get("title", ""),
            "tags": tags,
            "source": entry.get("link", ""),
            "author": entry.get("author", ""),
            "date": publishedDate.isoformat() if publishedDate else "",
            "text": _extractText(entry),
        })

    return jsonResponse


def main(cutoff: datetime.datetime | None = oneDayAgo) -> list[dict]:
    jsonResponse = []
    for row in getListofRssLinks(CSV_PATH):
        if not row:  # skip blank lines in the CSV
            continue
        url, tags = row[0], list(row[1:])
        jsonResponse.extend(getFullResponseFromFeed(url, tags, cutoff))

    return jsonResponse


def cli():
    parser = argparse.ArgumentParser(description="Scrape a list of news RSS feeds into JSON.")
    parser.add_argument("--run", action="store_true", help="Run the scraper and write the JSON file.")
    parser.add_argument("--debug", action="store_true", help="Print the raw JSON response.")
    parser.add_argument(
        "-d", "--days",
        type=int,
        default=1,
        help="Only keep posts from the last N days (default: 1).",
    )
    args = parser.parse_args()

    if args.run or args.debug:
        cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=args.days)
        jsonResponse = main(cutoff)
        if args.debug:
            print(json.dumps(jsonResponse, ensure_ascii=False, indent=2))
        if args.run:
            os.makedirs(folderpath, exist_ok=True)
            writePath = os.path.join(folderpath, str(datetime.date.today()) + "-news.json")
            with open(writePath, "w") as f:
                json.dump(jsonResponse, f, ensure_ascii=False, indent=2)
            print(f"wrote {len(jsonResponse)} articles to {writePath}")
            return jsonResponse
    else:
        parser.print_help()


if __name__ == "__main__":
    cli()
