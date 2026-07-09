import os
import json
import sqlite3

from src.substack.substack import setupURL


DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "substack.db")
DEFAULT_PRIORITY_PATH = os.path.join(os.path.dirname(__file__), "priority.txt")

SCHEMA = """
CREATE TABLE IF NOT EXISTS urls (
    handle TEXT PRIMARY KEY,
    url    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tags (
    handle TEXT NOT NULL,
    tag    TEXT NOT NULL,
    PRIMARY KEY (handle, tag)
);
"""


def connect(dbPath: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    return sqlite3.connect(dbPath)


def initDb(conn: sqlite3.Connection) -> None:
    with conn:
        conn.executescript(SCHEMA)


def insertCreator(
    conn: sqlite3.Connection,
    handle: str,
    tags: list[str] | None = None,
    url: str | None = None,
) -> str:
    if url is None:
        url = setupURL(handle)
    with conn:
        conn.execute("INSERT OR IGNORE INTO urls(handle, url) VALUES (?, ?)", (handle, url))
        for tag in (tags or []):
            conn.execute("INSERT OR IGNORE INTO tags(handle, tag) VALUES (?, ?)", (handle, tag))
    return url


def insertTag(conn: sqlite3.Connection, handle: str, tag: str) -> None:
    with conn:
        conn.execute("INSERT OR IGNORE INTO tags(handle, tag) VALUES (?, ?)", (handle, tag))


def getSubscribe(conn: sqlite3.Connection, path: str = DEFAULT_PRIORITY_PATH) -> None:
    with open(path) as f:
        handles = [line.strip() for line in f if line.strip()]

    with conn:
        conn.execute("DROP TABLE IF EXISTS priority")
        conn.execute("CREATE TABLE priority (handle TEXT)")
        conn.executemany("INSERT INTO priority(handle) VALUES (?)", [(h,) for h in handles])


def loadFromConfig(conn: sqlite3.Connection, configPath: str) -> int:
    with open(configPath) as f:
        creators = json.load(f)

    for entry in creators:
        handle = entry["handle"]
        insertCreator(conn, handle, tags=entry.get("tags"), url=entry.get("url"))
    return len(creators)


def getUrl(conn: sqlite3.Connection, handle: str) -> str | None:
    row = conn.execute("SELECT url FROM urls WHERE handle = ?", (handle,)).fetchone()
    return row[0] if row else None


def getTags(conn: sqlite3.Connection, handle: str) -> list[str]:
    rows = conn.execute("SELECT tag FROM tags WHERE handle = ?", (handle,)).fetchall()
    return [r[0] for r in rows]


def getHandlesByTag(conn: sqlite3.Connection, tag: str) -> list[str]:
    rows = conn.execute("SELECT handle FROM tags WHERE tag = ?", (tag,)).fetchall()
    return [r[0] for r in rows]

def run():
    conn = connect()
    initDb(conn)
