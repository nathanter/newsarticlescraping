import glob
import json
import os
import sys


#main file that congregates all the streams

# each scraper writes its dated json files into one folder at the project root.
# (folder, x) — x is how many of the most recent daily files to read for that
# stream. per-stream because the streams fill at very different rates, so the
# number of days it takes to reach a useful amount of text differs by source.
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
STREAM_FOLDERS = {
    "hn": ("hnposts", 2),
    "news": ("newsposts", 1),
    "substack": ("substacks", 1),
}


def recentFiles(folder: str, x: int) -> list[str]:
    # files are named "<YYYY-MM-DD>-<suffix>.json"; the date sorts auto
    # so the last x names are the newest x.
    # glob returns paths in arbitrary order, so we sort explicitly.
    paths = glob.glob(os.path.join(folder, "*.json"))
    return sorted(paths)[-x:]


def dedupBySource(articles: list[dict]) -> list[dict]:
    # the same post can land in several days' files (undated entries are kept on
    # every run, feeds overlap at day boundaries), so keep the first per source link.
    seen = set()
    unique = []
    for article in articles:
        key = article.get("source", "")
        if key and key in seen:
            continue
        if key:
            seen.add(key)
        unique.append(article)
    return unique


def balanceByTag(articles: list[dict], excluded: list[str] = [], quota: int = 3) -> list[dict]:
    excluded = set(excluded)
    kept = [a for a in articles if not excluded.intersection(a.get("tags", []))]

    # bucket by tag; a multi-tag article lands in each of its buckets
    keep = []
    bucketsCounts: dict[str,int ] = {}
    for article in kept:
        overflowedtags = [tag for tag in article.get("tags", []) if bucketsCounts.get(tag,0) > quota]
        if len(overflowedtags) == len(article.get("tags", [])):
            continue

        for tag in article.get("tags", []):
            bucketsCounts[tag] = bucketsCounts.get(tag, 0) + 1
        
        keep.append(article)
    


    return keep



def loadRecent(x: int | None = None) -> dict[str, list[dict]]:
    # read the most recent daily files from each source's folder and return the
    # articles keyed by stream, so the sources stay separable (never merged).
    # each stream uses its own x from STREAM_FOLDERS; passing x here overrides
    # all of them, which keeps the old loadRecent(3) call style working.
    streams = {}
    for stream, (folder, streamX) in STREAM_FOLDERS.items():
        articles = []
        for path in recentFiles(os.path.join(PROJECT_ROOT, folder), x if x is not None else streamX):
            with open(path) as f:
                articles.extend(json.load(f))
        streams[stream] = dedupBySource(articles)
    return streams


