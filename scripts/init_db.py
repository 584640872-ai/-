import os
import sqlite3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
path = Path(os.environ.get("DATABASE_PATH", str(ROOT / ".data/leads.sqlite3")))
path.parent.mkdir(parents=True, exist_ok=True)
with sqlite3.connect(path) as db:
    db.execute("PRAGMA foreign_keys = ON")
    db.execute("CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY, applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
    for migration in sorted((ROOT / "db/migrations").glob("*.sql")):
        if not db.execute("SELECT 1 FROM schema_migrations WHERE version=?", (migration.name,)).fetchone():
            version = migration.name.replace("'", "''")
            db.executescript("BEGIN IMMEDIATE;\n" + migration.read_text() +
                f"\nINSERT INTO schema_migrations(version) VALUES ('{version}');\nCOMMIT;")
print("数据库初始化完成")
