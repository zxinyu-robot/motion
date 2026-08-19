#!/usr/bin/env python3
"""Import motion/ project docs into local Zotero: collections + tags + stored attachments.

Requires Zotero to be **closed** (SQLite lock). Idempotent: skips files already linked in target collection.
"""

from __future__ import annotations

import hashlib
import mimetypes
import random
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/home/ubuntu/Downloads/motion")
ZOTERO_DATA = Path("/home/ubuntu/Zotero")
DB_PATH = ZOTERO_DATA / "zotero.sqlite"
STORAGE = ZOTERO_DATA / "storage"
LIBRARY_ID = 1
ROOT_COLLECTION_NAME = "motion"

SKIP_DIRS = {
    ".git",
    ".cursor",
    ".venv-docx",
    ".vscode",
    "__pycache__",
    "node_modules",
    ".mplcache",
}
IMPORT_EXTS = {
    ".md",
    ".pdf",
    ".txt",
    ".docx",
    ".bib",
    ".ris",
    ".sh",
    ".py",
    ".svg",
    ".png",
    ".json",
}
KEY_CHARS = "23456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ATTACHMENT_TYPE = 3
TITLE_FIELD = 1


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def gen_key(existing: set[str]) -> str:
    while True:
        key = "".join(random.choice(KEY_CHARS) for _ in range(8))
        if key not in existing:
            existing.add(key)
            return key


def is_zotero_running() -> bool:
    try:
        import subprocess

        out = subprocess.run(
            ["pgrep", "-f", "/opt/zotero/zotero-bin"],
            capture_output=True,
            text=True,
        )
        return out.returncode == 0
    except Exception:
        return False


def iter_import_files() -> list[tuple[Path, Path]]:
    """Return (absolute_path, relative_dir_from_root) pairs."""
    results: list[tuple[Path, Path]] = []
    for dirpath, dirnames, filenames in os_walk_sorted(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        base = Path(dirpath)
        rel_dir = base.relative_to(ROOT)
        for name in sorted(filenames):
            path = base / name
            if path.suffix.lower() not in IMPORT_EXTS:
                continue
            if ".mplcache" in path.parts:
                continue
            results.append((path, rel_dir))
    return results


def os_walk_sorted(root: Path):
    import os

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        yield dirpath, dirnames, filenames


def load_existing_keys(cur: sqlite3.Cursor) -> set[str]:
    keys: set[str] = set()
    for table in ("items", "collections"):
        cur.execute(f"SELECT key FROM {table}")
        keys.update(row[0] for row in cur.fetchall())
    return keys


def get_or_create_value(cur: sqlite3.Cursor, value: str) -> int:
    cur.execute("SELECT valueID FROM itemDataValues WHERE value=?", (value,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute("INSERT INTO itemDataValues (value) VALUES (?)", (value,))
    return cur.lastrowid


def ensure_root_collection(cur: sqlite3.Cursor, keys: set[str]) -> int:
    cur.execute(
        "SELECT collectionID FROM collections WHERE collectionName=? AND parentCollectionID IS NULL",
        (ROOT_COLLECTION_NAME,),
    )
    row = cur.fetchone()
    if row:
        return row[0]
    now = utc_now()
    key = gen_key(keys)
    cur.execute(
        """INSERT INTO collections
           (collectionName, parentCollectionID, clientDateModified, libraryID, key, version, synced)
           VALUES (?, NULL, ?, ?, ?, 0, 0)""",
        (ROOT_COLLECTION_NAME, now, LIBRARY_ID, key),
    )
    return cur.lastrowid


def ensure_collection_path(
    cur: sqlite3.Cursor,
    keys: set[str],
    root_id: int,
    rel_dir: Path,
    cache: dict[Path, int],
) -> int:
    if rel_dir == Path("."):
        return root_id
    if rel_dir in cache:
        return cache[rel_dir]

    parent_dir = rel_dir.parent
    parent_id = ensure_collection_path(cur, keys, root_id, parent_dir, cache)
    name = rel_dir.name

    cur.execute(
        """SELECT collectionID FROM collections
           WHERE collectionName=? AND parentCollectionID=?""",
        (name, parent_id),
    )
    row = cur.fetchone()
    if row:
        cache[rel_dir] = row[0]
        return row[0]

    now = utc_now()
    key = gen_key(keys)
    cur.execute(
        """INSERT INTO collections
           (collectionName, parentCollectionID, clientDateModified, libraryID, key, version, synced)
           VALUES (?, ?, ?, ?, ?, 0, 0)""",
        (name, parent_id, now, LIBRARY_ID, key),
    )
    cid = cur.lastrowid
    cache[rel_dir] = cid
    return cid


def ensure_tag(cur: sqlite3.Cursor, name: str, cache: dict[str, int]) -> int:
    if name in cache:
        return cache[name]
    cur.execute("SELECT tagID FROM tags WHERE name=?", (name,))
    row = cur.fetchone()
    if row:
        cache[name] = row[0]
        return row[0]
    cur.execute("INSERT INTO tags (name) VALUES (?)", (name,))
    cache[name] = cur.lastrowid
    return cache[name]


def existing_titles_in_collection(cur: sqlite3.Cursor, collection_id: int) -> set[str]:
    cur.execute(
        """
        SELECT idv.value
        FROM collectionItems ci
        JOIN itemData id ON id.itemID = ci.itemID
        JOIN itemDataValues idv ON id.valueID = idv.valueID
        WHERE ci.collectionID=? AND id.fieldID=?
        """,
        (collection_id, TITLE_FIELD),
    )
    return {row[0] for row in cur.fetchall()}


def import_file(
    cur: sqlite3.Cursor,
    keys: set[str],
    file_path: Path,
    collection_id: int,
    rel_dir: Path,
    tag_cache: dict[str, int],
    order_index: dict[int, int],
    existing_titles: set[str],
) -> bool:
    title = file_path.stem
    if title in existing_titles:
        return False

    now = utc_now()
    item_key = gen_key(keys)
    value_id = get_or_create_value(cur, title)

    cur.execute(
        """INSERT INTO items
           (itemTypeID, dateAdded, dateModified, clientDateModified, libraryID, key, version, synced)
           VALUES (?, ?, ?, ?, ?, ?, 0, 0)""",
        (ATTACHMENT_TYPE, now, now, now, LIBRARY_ID, item_key),
    )
    item_id = cur.lastrowid

    cur.execute(
        "INSERT INTO itemData (itemID, fieldID, valueID) VALUES (?, ?, ?)",
        (item_id, TITLE_FIELD, value_id),
    )

    dest_dir = STORAGE / item_key
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / file_path.name
    shutil.copy2(file_path, dest_file)

    content_type, _ = mimetypes.guess_type(str(file_path))
    if not content_type:
        content_type = "application/octet-stream"

    cur.execute(
        """INSERT INTO itemAttachments
           (itemID, parentItemID, linkMode, contentType, charsetID, path, syncState,
            storageModTime, storageHash, lastProcessedModificationTime, lastRead)
           VALUES (?, NULL, 0, ?, NULL, ?, 0, NULL, NULL, NULL, NULL)""",
        (item_id, content_type, f"storage:{file_path.name}"),
    )

    idx = order_index.get(collection_id, 0)
    cur.execute(
        "INSERT INTO collectionItems (collectionID, itemID, orderIndex) VALUES (?, ?, ?)",
        (collection_id, item_id, idx),
    )
    order_index[collection_id] = idx + 1

    # Tags: root + folder path + leaf folder name
    tag_names = [ROOT_COLLECTION_NAME]
    if rel_dir != Path("."):
        tag_names.append(str(rel_dir).replace("\\", "/"))
        tag_names.append(rel_dir.name)
    for tag_name in tag_names:
        tag_id = ensure_tag(cur, tag_name, tag_cache)
        cur.execute(
            "INSERT OR IGNORE INTO itemTags (itemID, tagID, type) VALUES (?, ?, 0)",
            (item_id, tag_id),
        )

    existing_titles.add(title)
    return True


def main() -> int:
    if is_zotero_running():
        print("ERROR: Zotero is running. Close Zotero first, then rerun this script.", file=sys.stderr)
        return 1

    if not DB_PATH.exists():
        print(f"ERROR: Zotero DB not found: {DB_PATH}", file=sys.stderr)
        return 1

    files = iter_import_files()
    print(f"Found {len(files)} importable files under {ROOT}")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    keys = load_existing_keys(cur)
    root_id = ensure_root_collection(cur, keys)

    coll_cache: dict[Path, int] = {Path("."): root_id}
    tag_cache: dict[str, int] = {}
    order_index: dict[int, int] = {}

    # Phase 1: create all collections (tags/folders)
    all_dirs: set[Path] = {Path(".")}
    for _, rel_dir in files:
        parts = rel_dir.parts
        for i in range(len(parts)):
            all_dirs.add(Path(*parts[: i + 1]) if parts else Path("."))

    for rel_dir in sorted(all_dirs, key=lambda p: (len(p.parts), str(p))):
        ensure_collection_path(cur, keys, root_id, rel_dir, coll_cache)

    conn.commit()
    print(f"Collections ready: {len(coll_cache)} (root = '{ROOT_COLLECTION_NAME}')")

    # Phase 2: import files
    imported = 0
    skipped = 0
    titles_cache: dict[int, set[str]] = {}

    for file_path, rel_dir in files:
        collection_id = ensure_collection_path(cur, keys, root_id, rel_dir, coll_cache)
        if collection_id not in titles_cache:
            titles_cache[collection_id] = existing_titles_in_collection(cur, collection_id)
        if import_file(
            cur,
            keys,
            file_path,
            collection_id,
            rel_dir,
            tag_cache,
            order_index,
            titles_cache[collection_id],
        ):
            imported += 1
        else:
            skipped += 1

    cur.execute("UPDATE libraries SET version = version + 1 WHERE libraryID=?", (LIBRARY_ID,))
    conn.commit()
    conn.close()

    print(f"Done. Imported: {imported}, skipped (duplicate title in collection): {skipped}")
    print(f"Tags created/used: {len(tag_cache)}")
    print("Start Zotero to view the 'motion' library tree.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
