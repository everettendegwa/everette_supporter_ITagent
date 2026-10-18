import json
import re
import sqlite3
from pathlib import Path
from typing import Any


class GuideRepository:
    def __init__(self, database_path: Path, include_drafts: bool = False):
        self.database_path = database_path
        self.include_drafts = include_drafts

    def _connect(self) -> sqlite3.Connection:
        if not self.database_path.exists():
            raise FileNotFoundError(f"Guide database not found: {self.database_path}")
        con = sqlite3.connect(f"file:{self.database_path.resolve().as_posix()}?mode=ro", uri=True)
        con.row_factory = sqlite3.Row
        return con

    @staticmethod
    def _sources(con: sqlite3.Connection, guide_id: str) -> list[dict[str, str]]:
        rows = con.execute(
            """SELECT s.title, s.url, s.publisher
               FROM source s JOIN guide_source gs USING (source_id)
               WHERE gs.guide_id = ? ORDER BY s.title""",
            (guide_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def search(self, query: str, limit: int = 8) -> list[dict[str, Any]]:
        # Quote token-by-token so user punctuation cannot alter the FTS query syntax.
        tokens = re.findall(r"[\w-]+", query, flags=re.UNICODE)[:12]
        if not tokens:
            return []
        fts_query = " OR ".join(f'"{token.replace(chr(34), chr(34) * 2)}"' for token in tokens)
        with self._connect() as con:
            try:
                status_filter = "" if self.include_drafts else "AND g.status = 'approved'"
                rows = con.execute(
                    """SELECT g.* FROM guide_search f
                       JOIN guide g USING (guide_id)
                       WHERE guide_search MATCH ? """ + status_filter + """
                       ORDER BY bm25(guide_search) LIMIT ?""",
                    (fts_query, limit),
                ).fetchall()
            except sqlite3.OperationalError:
                rows = []
            if not rows:
                # LIKE fallback supports a database that was rebuilt without FTS5.
                pattern = f"%{tokens[0]}%"
                status_filter = "" if self.include_drafts else "AND status = 'approved'"
                rows = con.execute(
                    "SELECT * FROM guide WHERE (title LIKE ? OR summary LIKE ?) " + status_filter + " ORDER BY title LIMIT ?",
                    (pattern, pattern, limit),
                ).fetchall()
            return [self._summary(con, row) for row in rows]

    def get(self, guide_id: str) -> dict[str, Any] | None:
        with self._connect() as con:
            row = con.execute("SELECT * FROM guide WHERE guide_id = ?", (guide_id,)).fetchone()
            if row is None:
                return None
            if not self.include_drafts and row["status"] != "approved":
                return None
            result = self._summary(con, row)
            result.update(
                symptoms=json.loads(row["symptoms_json"]),
                steps=json.loads(row["steps_json"]),
                cautions=json.loads(row["cautions_json"]),
                escalation=row["escalation"],
                tags=[r[0] for r in con.execute(
                    "SELECT tag FROM guide_tag WHERE guide_id = ? ORDER BY tag", (guide_id,)
                ).fetchall()],
            )
            return result

    def _summary(self, con: sqlite3.Connection, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "guide_id": row["guide_id"],
            "title": row["title"],
            "category": row["category"],
            "applicable_os": row["applicable_os"],
            "summary": row["summary"],
            "status": row["status"],
            "sources": self._sources(con, row["guide_id"]),
        }

