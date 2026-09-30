import sqlite3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'var' / 'development.sqlite3'

def connect():
    DB.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB)
    conn.execute('PRAGMA foreign_keys=ON')
    return conn

def initialize():
    with connect() as conn:
        conn.executescript((ROOT / 'database' / 'schema.sql').read_text())
    return DB

if __name__ == '__main__':
    print(initialize())
