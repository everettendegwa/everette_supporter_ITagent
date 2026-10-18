-- Schema is already applied in windows_troubleshooting.db.
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
