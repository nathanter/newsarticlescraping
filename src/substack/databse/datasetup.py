import sys

from src.substack.databse.ssdb import SubstackDB


def parseLine(line: str) -> tuple[str, list[str]] | None:
    line = line.strip()
    if not line:
        return None
    name, _, tagPart = line.partition(":")
    name = name.strip()
    if not name:
        return None
    tags = [t.strip() for t in tagPart.split(",") if t.strip()]
    return name, tags


def loadCreators(db: SubstackDB, path: str) -> int:
    count = 0
    with open(path) as f:
        for line in f:
            parsed = parseLine(line)
            if parsed is None:
                continue
            name, tags = parsed
            db.insertCreator(name, tags=tags)
            count += 1
    return count


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: python -m src.substack.databse.datasetup <file>")
        sys.exit(1)

    path = sys.argv[1]
    db = SubstackDB()
    try:
        n = loadCreators(db, path)
        print(f"Loaded {n} creator(s) from {path}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
