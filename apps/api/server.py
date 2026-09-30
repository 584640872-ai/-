"""零依赖本地骨架：仅开放健康检查和模块索引，不处理患者信息。"""
import json
import os
import sqlite3
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = Path(__file__).resolve().parents[2]
DB = Path(os.environ.get("DATABASE_PATH", str(ROOT / ".data/leads.sqlite3")))
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            try:
                with sqlite3.connect(f"file:{DB}?mode=ro", uri=True) as db:
                    db.execute("SELECT 1 FROM schema_migrations LIMIT 1").fetchone()
                self.respond(200, {"status": "ok", "database": "ready", "mode": "development-skeleton"})
            except sqlite3.Error:
                self.respond(503, {"status": "not_ready", "hint": "先运行 scripts/init_db.py"})
        elif self.path == "/api/v1/modules":
            self.respond(200, {"implemented": ["health", "schema", "assignment_rules", "workflow_rules", "permission_rules"],
                "planned": ["auth", "lead_intake", "assignment_transactions", "consultation", "exceptions", "dashboard", "audit"]})
        elif self.path == "/":
            content = (ROOT / "apps/web/index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(content)
        else:
            self.respond(404, {"error": "not_implemented", "message": "业务 API 尚未实现"})
    def respond(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    print(f"开发骨架：http://{host}:{port}", flush=True)
    HTTPServer((host, port), Handler).serve_forever()
