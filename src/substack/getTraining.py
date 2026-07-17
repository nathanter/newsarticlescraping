import argparse
import datetime
import json
import os

from src.substack import scraper
from src.substack import substack
from src.substack.databse import datasetup
from src.substack.databse import ssdb


# anchor the output folder to the project root (../../ from src/substack) so the
# write lands in the same place no matter which cwd the tool is launched from
BASE_DIR = os.path.dirname(__file__)
folderpath = os.path.join(BASE_DIR, "..", "..", "substacks")

# hand-curated creators live alongside the db, one per line: "handle: Tag1, Tag2"
CREATOR_RECS_PATH = os.path.join(BASE_DIR, "databse", "creatorRecs")




def _collectArticles(db: ssdb.SubstackDB, handles: list[str]) -> list[dict]:

    # only keep posts from the last 7 days; getFullResponseFromSubStack skips
    # anything published before this cutoff
    oneWeekAgo = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(weeks=1)

    massResponse = []
    for handle in handles:
        url = db.getUrl(handle)
        tags = db.getTags(handle)

        try:
            articles = substack.getFullResponseFromSubStack(url, oneWeekAgo)
        except substack.FeedNotFoundException:
            # url is permanently gone (404/410) — drop it so we stop retrying
            db.deleteCreator(handle)
            continue
        except substack.SubstackException:
            # transient (block/timeout/empty) — keep the creator, skip this run
            continue

        for article in articles:
            article["tags"] = tags
        massResponse.extend(articles)

    return massResponse


def getTaggedArticles(tag: str) -> list[dict]:
    db = ssdb.SubstackDB()
    try:
        handles = db.getHandlesByTag(tag)
        if not handles:
            raise ValueError(f"no creators found for tag '{tag}'")
        return _collectArticles(db, handles)
    finally:
        db.close()



def getMassArticles() -> list[dict]:
    # every creator in the db, each article stamped with that creator's tags
    db = ssdb.SubstackDB()
    try:
        return _collectArticles(db, db.getAllHandles())
    finally:
        db.close()


def countHandles() -> int:
    db = ssdb.SubstackDB()
    try:
        return db.countHandles()
    finally:
        db.close()


def dbsetup() -> None:
    # use the scraper to add creators, each tagged with its explore category
    db = ssdb.SubstackDB()
    try:
        # first pull in the hand-curated creators from creatorRecs, if present
        if os.path.exists(CREATOR_RECS_PATH):
            loaded = datasetup.loadCreators(db, CREATOR_RECS_PATH)
            print(f"loaded {loaded} creator(s) from creatorRecs")
        else:
            print(f"no creatorRecs file at {CREATOR_RECS_PATH}, skipping manual load")

        cats = scraper.list_all_categories()
        progress = 0
        for categoryName, categoryId in cats.items():
            for handle in scraper.getUsersinCategory(categoryId):
                progress += 1
                print(f"progress: {progress}")
                db.insertCreator(handle, [categoryName], substack.setupURL(handle))
    finally:
        db.close()


def writeArticles(articles: list[dict], path: str) -> str:
    os.makedirs(folderpath, exist_ok=True)
    path = os.path.normpath(os.path.join(folderpath, str(datetime.date.today()) + "-" + path))
    with open(path, "w") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="getTraining",
        description="Populate the Substack creator database and pull articles from it.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # adding creators/tags to the db is its own command, separate from fetching
    sub.add_parser(
        "setup",
        help="Scrape categories and add creators + tags to the database.",
    )

    articlesParser = sub.add_parser(
        "articles",
        help="Fetch articles from the db's creators and write them to a JSON file.",
    )
    articlesParser.add_argument(
        "-t", "--tag",
        help="Only fetch creators with this tag (default: all creators).",
    )
    articlesParser.add_argument(
        "-o", "--out",
        default="articles.json",
        help="Output JSON file path (default: articles.json).",
    )

    sub.add_parser(
        "count",
        help="Print the number of creators (handles) in the database.",
    )

    sub.add_parser(
        "categories",
        help="List all Substack categories (the possible tags) with their ids.",
    )

    args = parser.parse_args()

    if args.command == "setup":
        dbsetup()
        print("Database populated.")
    elif args.command == "articles":
        articles = getTaggedArticles(args.tag) if args.tag else getMassArticles()
        out = writeArticles(articles, args.out)
        print(f"Wrote {len(articles)} article(s) to {out}")
    elif args.command == "count":
        print(countHandles())
    elif args.command == "categories":
        for name, cid in sorted(scraper.list_all_categories().items()):
            print(f"{cid:5}  {name}")


if __name__ == "__main__":
    main()












