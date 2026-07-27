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


# raised when a feed in rsss.csv can't be read — dead url, block, or malformed xml.
# mirrors SubstackException (substack.py:13) so both scrapers signal a bad feed the
# same way; carries the url and http status so the caller can report which line failed.
class FeedException(Exception):
    def __init__(self, feedUrl: str, status=None, reason=None):
        self.feedUrl = feedUrl
        self.status = status

        super().__init__(f"{feedUrl} : status={status}")

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


def writeRssLinks(filePath: str, urlAndTags: list[tuple[str, ...]]) -> None:
    # inverse of getListofRssLinks — same "url, tag1, tag2, ..." row per line.
    with open(filePath, "w", newline="") as f:
        csv.writer(f).writerows(urlAndTags)


def extractText(entry) -> str:

    rawHTML = entry.get("content", [{}])[0].get("value")
    if rawHTML is None:
        rawHTML = entry.get("summary", "")
    return BeautifulSoup(rawHTML, "html.parser").get_text(separator="\n").strip()


# Takes one feed URL plus its tags, returns its entries in the readme JSON shape.
# cutoff, when given, keeps only entries published strictly after it.
def getFullResponseFromFeed(feedUrl: str, tags: list[str], cutoff: datetime.datetime | None = None) -> list[dict]:
    jsonResponse = []
    rss = feedparser.parse(feedUrl, agent=HEADERS["User-Agent"])

    # bozo alone isn't fatal — plenty of feeds parse with warnings and still hand
    # back entries. no entries as well means there's nothing to salvage.
    if rss.bozo and not rss.entries:
        raise FeedException(feedUrl, rss.get("status"), rss.get("bozo_exception"))

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
            "text": extractText(entry),
        })

    return jsonResponse


def main(cutoff: datetime.datetime | None = oneDayAgo) -> list[dict]:
    jsonResponse = []
    successfullLinks = []
    failed = False
    for row in getListofRssLinks(CSV_PATH):
        if not row:  # skip blank lines in the CSV
            continue
        url, tags = row[0], list(row[1:])
        # one unreadable feed shouldn't cost us the rest, so record it and carry on
        try:
            jsonResponse.extend(getFullResponseFromFeed(url, tags, cutoff))
            successfullLinks.append(row)
        except FeedException as exc:
            print("feed failure: " + str(exc))
            failed = True


    # only rewrite when something actually failed, so a clean run leaves the file alone
    if failed:
        writeRssLinks(CSV_PATH, successfullLinks)
    

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
