import feedparser
import argparse
import json
from datetime import date



feedUrl = "https://news.ycombinator.com/rss"

folderpath = "hnposts/"
def main():
    jsonResponse = []
    rss = feedparser.parse(feedUrl)

    for entry in rss.entries:
        jsonResponse.append({
            "title": entry.get("title"),
            "link": entry.get("comments"),
            "date": entry.get("published"),
            "author": None,
            "tags" : ["Technology","Science"],
            "text": entry.get("title")

        })

    return jsonResponse


def cli():
    parser = argparse.ArgumentParser(description="Scrape the Hacker News RSS feed into JSON.")
    parser.add_argument("--run", action="store_true", help="Run the scraper.")
    parser.add_argument("--debug", action="store_true", help="Print the raw JSON response.")
    args = parser.parse_args()

    if args.run or args.debug:
        jsonResponse = main()
        if args.debug:
            print(json.dumps(jsonResponse, indent=2))
        if args.run:
            writePath = folderpath + str(date.today()) + "-hn.json"
            with open(writePath, "w") as f:
                json.dump(jsonResponse, f, ensure_ascii=False, indent=2)

    else:
        parser.print_help()


if __name__ == "__main__":
    cli()
