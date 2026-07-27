import glob
import json
import os
import sys


#main file that congregates all the streams

# each scraper writes its dated json files into one folder at the project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
STREAM_FOLDERS = {
    "hn": "hnposts",
    "news": "newsposts",
    "substack": "substacks",
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


def loadRecent(x: int) -> dict[str, list[dict]]:
    # read the most recent x daily files from each source's folder and return the
    # articles keyed by stream, so the sources stay separable (never merged).
    streams = {}
    for stream, folder in STREAM_FOLDERS.items():
        articles = []
        for path in recentFiles(os.path.join(PROJECT_ROOT, folder), x):
            with open(path) as f:
                articles.extend(json.load(f))
        streams[stream] = dedupBySource(articles)
    return streams


if __name__ == "__main__":
    # manual check: load the last x files per source (default 1), still split by stream
    x = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    print(json.dumps(loadRecent(x), ensure_ascii=False, indent=2))
