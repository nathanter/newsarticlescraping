import os
import json
import sqlite3
from ..substack import setupURL


DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "substack.db")
DEFAULT_PRIORITY_PATH = os.path.join(os.path.dirname(__file__), "priority.txt")


class SubstackDB:
    SCHEMA = """
    CREATE TABLE IF NOT EXISTS urls (
        handle TEXT PRIMARY KEY,
        url    TEXT NOT NULL,
        rating INTEGER NOT NULL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS tags (
        handle TEXT NOT NULL,
        tag    TEXT NOT NULL,
        PRIMARY KEY (handle, tag)
    );
    """

    def __init__(self, dbPath: str = DEFAULT_DB_PATH):
        self.conn = sqlite3.connect(dbPath)
        self.initDb()

    def initDb(self) -> None:
        with self.conn:
            self.conn.executescript(self.SCHEMA)

    def insertCreator(
        self,
        handle: str,
        tags: list[str] | None = None,
        url: str | None = None,
        rating: int = 0
    ) -> str:
        if url is None:
            url = setupURL(handle)
        with self.conn:
            # a creator can appear in several categories with different ratings;
            # keep the best (lowest) one. rating is NOT NULL, so MIN needs no COALESCE.
            self.conn.execute(
                "INSERT INTO urls(handle, url, rating) VALUES (?, ?, ?) "
                "ON CONFLICT(handle) DO UPDATE SET rating = MIN(excluded.rating, urls.rating)",
                (handle, url, rating),
            )
            for tag in (tags or []):
                self.conn.execute("INSERT OR IGNORE INTO tags(handle, tag) VALUES (?, ?)", (handle, tag))
        return url

    def insertTag(self, handle: str, tag: str) -> None:
        with self.conn:
            self.conn.execute("INSERT OR IGNORE INTO tags(handle, tag) VALUES (?, ?)", (handle, tag))

    def getSubscribe(self, path: str = DEFAULT_PRIORITY_PATH) -> None:
        with open(path) as f:
            handles = [line.strip() for line in f if line.strip()]

        with self.conn:
            self.conn.execute("DROP TABLE IF EXISTS priority")
            self.conn.execute("CREATE TABLE priority (handle TEXT)")
            self.conn.executemany("INSERT INTO priority(handle) VALUES (?)", [(h,) for h in handles])

    def deleteCreator(self, handle: str) -> None:
        with self.conn:
            self.conn.execute("DELETE FROM urls WHERE handle = ?", (handle,))
            self.conn.execute("DELETE FROM tags WHERE handle = ?", (handle,))

    def getAllHandles(self) -> list[str]:
        
        rows = self.conn.execute("SELECT handle FROM urls ORDER BY rating ASC").fetchall()
        return [r[0] for r in rows]

    def getUrl(self, handle: str) -> str | None:
        row = self.conn.execute("SELECT url FROM urls WHERE handle = ?", (handle,)).fetchone()
        return row[0] if row else None

    def getRating(self, handle: str) -> int | None:
        row = self.conn.execute("SELECT rating FROM urls WHERE handle = ?", (handle,)).fetchone()
        return row[0] if row else None

    def getTags(self, handle: str) -> list[str]:
        rows = self.conn.execute("SELECT tag FROM tags WHERE handle = ?", (handle,)).fetchall()
        return [r[0] for r in rows]

    def getHandlesByTag(self, tag: str) -> list[str]:
        # rating lives on urls, so join to sort; lower rating = better (best first)
        rows = self.conn.execute(
            "SELECT t.handle FROM tags t JOIN urls u ON u.handle = t.handle "
            "WHERE t.tag = ? ORDER BY u.rating ASC",
            (tag,),
        ).fetchall()
        return [r[0] for r in rows]

    def countHandles(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM urls").fetchone()[0]

    def close(self) -> None:
        self.conn.close()
