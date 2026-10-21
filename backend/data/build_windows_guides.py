import json
import sqlite3
from pathlib import Path

OUT = Path(__file__).resolve().parent
DB = OUT / "windows_troubleshooting.db"

guides = []

con = sqlite3.connect(DB)
con.executescript("""
PRAGMA foreign_keys=ON;
DROP TABLE IF EXISTS guide_search;
DROP TABLE IF EXISTS guide_tag;
DROP TABLE IF EXISTS guide_source;
DROP TABLE IF EXISTS guide;
DROP TABLE IF EXISTS source;
DROP TABLE IF EXISTS tag;
CREATE TABLE guide (
 guide_id TEXT PRIMARY KEY, title TEXT NOT NULL, category TEXT NOT NULL,
 applicable_os TEXT NOT NULL, summary TEXT NOT NULL,
 symptoms_json TEXT NOT NULL, steps_json TEXT NOT NULL,
 cautions_json TEXT NOT NULL, escalation TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'draft', reviewed_by TEXT,
 created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE source (
 source_id INTEGER PRIMARY KEY, title TEXT NOT NULL, url TEXT NOT NULL UNIQUE,
 publisher TEXT NOT NULL, accessed_at TEXT NOT NULL
);
CREATE TABLE guide_source (
 guide_id TEXT NOT NULL REFERENCES guide(guide_id) ON DELETE CASCADE,
 source_id INTEGER NOT NULL REFERENCES source(source_id),
 PRIMARY KEY(guide_id, source_id)
);
CREATE TABLE tag (
 tag TEXT PRIMARY KEY
);
CREATE TABLE guide_tag (
 guide_id TEXT NOT NULL REFERENCES guide(guide_id) ON DELETE CASCADE,
 tag TEXT NOT NULL REFERENCES tag(tag),
 PRIMARY KEY(guide_id, tag)
);
CREATE INDEX idx_guide_category ON guide(category);
CREATE VIRTUAL TABLE guide_search USING fts5(guide_id UNINDEXED, title, category, summary, symptoms, steps, tags);
""")
from datetime import date
today = date.today().isoformat()
all_sources = {}
for g in guides:
    con.execute("INSERT INTO guide VALUES (?,?,?,?,?,?,?,?,?,'draft',NULL,?,?)", (
        g["id"],g["title"],g["category"],g["os"],g["summary"],
        json.dumps(g["symptoms"],ensure_ascii=False),json.dumps(g["steps"],ensure_ascii=False),
        json.dumps(g["cautions"],ensure_ascii=False),g["escalate"],today,today))
    tags = {g["category"], "windows", "windows-10", "windows-11"}
    for word in g["title"].lower().replace("/"," ").split():
        if len(word)>3: tags.add(word.strip(".,!?"))
    for tag in sorted(tags):
        con.execute("INSERT OR IGNORE INTO tag VALUES (?)",(tag,))
        con.execute("INSERT INTO guide_tag VALUES (?,?)",(g["id"],tag))
    for title,url in g["sources"]:
        all_sources[url]=title
        con.execute("INSERT OR IGNORE INTO source(title,url,publisher,accessed_at) VALUES (?,?,?,?)",(title,url,"Microsoft Support",today))
        sid=con.execute("SELECT source_id FROM source WHERE url=?",(url,)).fetchone()[0]
        con.execute("INSERT INTO guide_source VALUES (?,?)",(g["id"],sid))
    con.execute("INSERT INTO guide_search VALUES (?,?,?,?,?,?,?)",(
        g["id"],g["title"],g["category"],g["summary"]," ".join(g["symptoms"])," ".join(g["steps"])," ".join(sorted(tags))))
con.commit()
con.close()

readme = """# Windows Troubleshooting Knowledge Base (Starter)

This SQLite database currently contains no guide records. Add only reviewed guide content before making it available to users.

## Files
- `windows_troubleshooting.db` — SQLite database with guides, source links, tags, and full-text search.
- `windows_troubleshooting.sql` — schema and example queries.
- `build_windows_guides.py` — reproducible database builder and seed content.

## Data model
- `guide`: problem summary, applicability, symptoms, ordered steps, cautions, escalation guidance, review status.
- `source`: official Microsoft Support reference and access date.
- `guide_source`: many-to-many link from guides to references.
- `tag` / `guide_tag`: searchable labels.
- `guide_search`: SQLite FTS5 full-text index for titles, summaries, symptoms, steps, and tags.

## Example
```sql
SELECT g.guide_id, g.title, g.summary
FROM guide_search s JOIN guide g USING (guide_id)
WHERE guide_search MATCH 'wifi internet';
```

## Important use notes
- Steps are paraphrased; open the linked Microsoft page for full, current instructions.
- Validate OS build/version and UI labels with the user because they change over time.
- Windows 10 support ended on October 14, 2025; tell users this when relevant and verify current lifecycle details before advising upgrades.
- Never let an AI tool execute arbitrary shell commands. Do not request passwords, one-time codes, BitLocker recovery keys, or Wi-Fi credentials.
- Destructive or privacy-sensitive steps (deletion, reset/reinstall, granting app access) need plain-language explanation and user approval.
- Do not add draft guide content to a production database.
"""
(OUT/"README_windows_troubleshooting.md").write_text(readme,encoding="utf-8")

sql = """-- Schema is already applied in windows_troubleshooting.db.
-- Find relevant guides:
SELECT g.guide_id, g.title, g.category, g.summary
FROM guide_search s JOIN guide g USING (guide_id)
WHERE guide_search MATCH 'wifi internet';

-- Retrieve a guide and official references:
SELECT g.title, g.applicable_os, g.summary, g.steps_json, g.cautions_json,
       s.title AS source_title, s.url
FROM guide g
JOIN guide_source gs USING (guide_id)
JOIN source s USING (source_id)
WHERE g.guide_id = 'wifi-no-internet';

-- Only serve human-approved material in production:
SELECT guide_id, title, summary, steps_json
FROM guide WHERE status = 'approved';
"""
(OUT/"windows_troubleshooting.sql").write_text(sql,encoding="utf-8")
print(f"Created {DB} with {len(guides)} guides and {len(all_sources)} unique official sources")
check = sqlite3.connect(DB)
assert check.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
assert check.execute("SELECT COUNT(*) FROM guide").fetchone()[0] == len(guides)
assert check.execute("SELECT COUNT(*) FROM guide_search").fetchone()[0] == 0
print("Verified SQLite integrity, guide count, and full-text search")
check.close()
