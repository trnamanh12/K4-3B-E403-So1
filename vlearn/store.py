import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


def now():
    return datetime.now(timezone.utc).isoformat()


class Store:
    def __init__(self, root: Path):
        self.root = root
        root.mkdir(parents=True, exist_ok=True)
        self.path = root / "sources.sqlite3"
        with self.connect() as db:
            db.executescript("""
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS snapshots (
                    id TEXT PRIMARY KEY, created TEXT NOT NULL, status TEXT NOT NULL,
                    config TEXT NOT NULL, collection TEXT, dimensions INTEGER);
                CREATE TABLE IF NOT EXISTS state (key TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS documents (
                    snapshot TEXT NOT NULL, id TEXT NOT NULL, data TEXT NOT NULL,
                    PRIMARY KEY(snapshot,id));
                CREATE TABLE IF NOT EXISTS units (
                    snapshot TEXT NOT NULL, id TEXT NOT NULL, data TEXT NOT NULL,
                    PRIMARY KEY(snapshot,id));
                CREATE TABLE IF NOT EXISTS chunks (
                    snapshot TEXT NOT NULL, id TEXT NOT NULL, data TEXT NOT NULL,
                    PRIMARY KEY(snapshot,id));
                CREATE TABLE IF NOT EXISTS embeddings (key TEXT PRIMARY KEY, vector TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS traces (id TEXT PRIMARY KEY, created TEXT, data TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY, trace_id TEXT NOT NULL, helpful INTEGER NOT NULL,
                    comment TEXT, created TEXT NOT NULL);
            """)

    @contextmanager
    def connect(self):
        with sqlite3.connect(self.path, timeout=30) as db:
            db.row_factory = sqlite3.Row
            yield db

    def snapshot(self, sid=None):
        with self.connect() as db:
            if sid is None:
                row = db.execute("SELECT value FROM state WHERE key='active'").fetchone()
                if not row:
                    raise ValueError("No active index. Run vlearn prepare and vlearn index first.")
                sid = row[0]
            row = db.execute("SELECT * FROM snapshots WHERE id=?", (sid,)).fetchone()
        if not row:
            raise ValueError("Unknown snapshot")
        result = dict(row)
        result["config"] = json.loads(result["config"])
        return result

    def save_snapshot(self, sid, config, documents, units, chunks):
        with self.connect() as db:
            db.execute("INSERT OR IGNORE INTO snapshots VALUES (?,?,?, ?,NULL,NULL)",
                       (sid, now(), "prepared", json.dumps(config)))
            for table, items in (("documents", documents), ("units", units), ("chunks", chunks)):
                db.executemany(f"INSERT OR IGNORE INTO {table} VALUES (?,?,?)",
                               [(sid, x["id"], json.dumps(x, ensure_ascii=False)) for x in items])

    def records(self, table, sid):
        if table not in {"documents", "units", "chunks"}:
            raise ValueError("Unknown record type")
        with self.connect() as db:
            return [json.loads(r[0]) for r in db.execute(
                f"SELECT data FROM {table} WHERE snapshot=? ORDER BY id", (sid,))]

    def record(self, table, sid, record_id):
        if table not in {"documents", "units", "chunks"}:
            raise ValueError("Unknown record type")
        with self.connect() as db:
            row = db.execute(f"SELECT data FROM {table} WHERE snapshot=? AND id=?",
                             (sid, record_id)).fetchone()
        if not row:
            raise ValueError("Source does not exist in this snapshot")
        return json.loads(row[0])

    def mark_indexed(self, sid, collection, dimensions):
        with self.connect() as db:
            db.execute("UPDATE snapshots SET status='indexed',collection=?,dimensions=? WHERE id=?",
                       (collection, dimensions, sid))

    def activate(self, sid):
        if self.snapshot(sid)["status"] != "indexed":
            raise ValueError("Only a fully indexed snapshot may be activated")
        with self.connect() as db:
            db.execute("INSERT OR REPLACE INTO state VALUES ('active',?)", (sid,))

    def cached_embedding(self, key):
        with self.connect() as db:
            row = db.execute("SELECT vector FROM embeddings WHERE key=?", (key,)).fetchone()
        return json.loads(row[0]) if row else None

    def cache_embedding(self, key, vector):
        with self.connect() as db:
            db.execute("INSERT OR REPLACE INTO embeddings VALUES (?,?)", (key, json.dumps(vector)))

    def trace(self, tid, data):
        with self.connect() as db:
            db.execute("INSERT OR REPLACE INTO traces VALUES (?,?,?)",
                       (tid, now(), json.dumps(data, ensure_ascii=False)))

    def feedback(self, tid, helpful, comment):
        with self.connect() as db:
            if not db.execute("SELECT 1 FROM traces WHERE id=?", (tid,)).fetchone():
                raise ValueError("Unknown trace_id")
            db.execute("INSERT INTO feedback(trace_id,helpful,comment,created) VALUES (?,?,?,?)",
                       (tid, helpful, comment, now()))
