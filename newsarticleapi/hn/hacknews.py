import feedparser
import argparse
import json
import os
from datetime import date, datetime, timedelta, timezone



feedUrl = "https://news.ycombinator.com/rss"


BASE_DIR = os.path.dirname(__file__)
folderpath = os.path.join(BASE_DIR, "..", "..", "hnposts")

oneDayAgo = datetime.now(timezone.utc) - timedelta(days=1)


# cutoff, when given, keeps only entries published strictly after it (default: last day).
def main(cutoff: datetime | None = oneDayAgo) -> list[dict]:
    jsonResponse = []
    rss = feedparser.parse(feedUrl)

    # a naive cutoff is assumed to be UTC so it compares cleanly with feed dates
    if cutoff is not None and cutoff.tzinfo is None:
        cutoff = cutoff.replace(tzinfo=timezone.utc)

    for entry in rss.entries:
        # feedparser gives published_parsed as a UTC struct_time, or None when undated;
        # emit ISO-8601 to match the other scrapers instead of the raw RSS date string
        publishedStruct = entry.get("published_parsed")
        publishedDate = (
            datetime(*publishedStruct[:6], tzinfo=timezone.utc)
            if publishedStruct else None
        )

        # skip dated entries at/before the cutoff; undated entries have no date to
        # test against, so they're always kept (matches the other scrapers)
        if cutoff is not None and publishedDate is not None and publishedDate <= cutoff:
            continue

        jsonResponse.append({
            "title": entry.get("title", ""),
            "tags": ["Technology", "Science"],
            "source": entry.get("comments", ""),
            "author": "",
            "date": publishedDate.isoformat() if publishedDate else "",
            "text": entry.get("title", ""),
        })

    return jsonResponse


def cli():
    parser = argparse.ArgumentParser(description="Scrape the Hacker News RSS feed into JSON.")
    parser.add_argument("--run", action="store_true", help="Run the scraper.")
    parser.add_argument("--debug", action="store_true", help="Print the raw JSON response.")
    parser.add_argument(
        "-d", "--days",
        type=int,
        default=1,
        help="Only keep posts from the last N days (default: 1).",
    )
    args = parser.parse_args()

    if args.run or args.debug:
        cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
        jsonResponse = main(cutoff)
        if args.debug:
            print(json.dumps(jsonResponse, indent=2))
        if args.run:
            os.makedirs(folderpath, exist_ok=True)
            writePath = os.path.normpath(
                os.path.join(folderpath, str(date.today()) + "-hn.json")
            )
            with open(writePath, "w") as f:
                json.dump(jsonResponse, f, ensure_ascii=False, indent=2)

            return jsonResponse

    else:
        parser.print_help()


if __name__ == "__main__":
    cli()

