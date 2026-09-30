import sqlite3, unittest
from pathlib import Path
class SchemaTests(unittest.TestCase):
    def test_schema_is_repeatable(self):
        conn=sqlite3.connect(':memory:')
        sql=(Path(__file__).resolve().parents[1]/'database/schema.sql').read_text()
        conn.executescript(sql)
        conn.executescript(sql)
        self.assertEqual(conn.execute('PRAGMA foreign_key_check').fetchall(),[])
        self.assertEqual(conn.execute('SELECT version FROM schema_migrations').fetchone()[0],'001')
