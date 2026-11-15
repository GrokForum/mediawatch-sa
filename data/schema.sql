-- MediaWatch SA schema v0.4-draft (primary scores + secondary lean_scores)
-- Hierarchy: publication > person > (article | public_post) > finding
-- Times stored as UTC ISO-8601; display in Africa/Johannesburg (SAST, UTC+2).

PRAGMA foreign_keys = ON;

CREATE TABLE publications (
  id              TEXT PRIMARY KEY,           -- slug, e.g. 'news24'
  name            TEXT NOT NULL,
  url             TEXT NOT NULL,
  owner_group     TEXT,
  owner_fact_label TEXT CHECK (owner_fact_label IN (
                    'Proven','Established','Alleged','Disputed','Not established'
                  )),
  language        TEXT NOT NULL,              -- EN | AF | multi
  editor_in_chief TEXT,
  editor_source_url TEXT,
  editor_checked_on TEXT,                     -- YYYY-MM-DD
  status          TEXT DEFAULT 'active',      -- active | archive_only | closed
  notes           TEXT
);

CREATE TABLE people (
  id              TEXT PRIMARY KEY,
  full_name       TEXT NOT NULL,
  role            TEXT NOT NULL,              -- public role only
  publication_id  TEXT REFERENCES publications(id),
  x_handle        TEXT,                       -- without @; null if unverified
  x_user_id       TEXT,
  x_handle_source_url TEXT,
  x_handle_checked_on TEXT,
  notes           TEXT
);

CREATE TABLE articles (
  id              TEXT PRIMARY KEY,
  publication_id  TEXT NOT NULL REFERENCES publications(id),
  author_person_id TEXT REFERENCES people(id),
  headline        TEXT,
  url             TEXT NOT NULL UNIQUE,
  published_at    TEXT NOT NULL,
  published_at_precision TEXT CHECK (published_at_precision IS NULL OR published_at_precision IN
                    ('date','datetime')),              -- date = calendar date only
  byline_raw      TEXT,
  section         TEXT,
  fetched_at      TEXT,
  verification_status TEXT DEFAULT 'verified'
                      CHECK (verification_status IN ('verified','unverified','seed_lead'))
);

CREATE TABLE public_posts (
  id              TEXT PRIMARY KEY,           -- prefer X snowflake id as text
  person_id       TEXT NOT NULL REFERENCES people(id),
  publication_id  TEXT REFERENCES publications(id), -- newsroom affiliation if any
  platform        TEXT NOT NULL DEFAULT 'x',
  url             TEXT NOT NULL UNIQUE,
  text            TEXT NOT NULL,
  posted_at       TEXT NOT NULL,              -- UTC ISO-8601
  metrics_json    TEXT,                       -- snapshot JSON
  repost_of_post_id TEXT REFERENCES public_posts(id), -- Cavus: RT = own amplification finding on reposter; no weight on original
  quoted_post_url TEXT,
  fetched_at      TEXT,
  verification_status TEXT DEFAULT 'verified'
                      CHECK (verification_status IN ('verified','unverified','seed_lead')),
  credit          TEXT                        -- e.g. 'AGOA SA casebook, Case 1'
);

CREATE TABLE findings (
  id              TEXT PRIMARY KEY,
  article_id      TEXT REFERENCES articles(id),
  public_post_id  TEXT REFERENCES public_posts(id),
  publication_id  TEXT NOT NULL REFERENCES publications(id),
  person_id       TEXT REFERENCES people(id),
  actor           TEXT NOT NULL,
  direction       TEXT NOT NULL CHECK (direction IN ('FOR','AGAINST')),
  driver          TEXT NOT NULL CHECK (driver IN (
                    'loaded_label','one_sided_sourcing','missing_right_of_reply',
                    'omission','framing','headline_body_gap','factual_error','correction'
                  )),
  quote           TEXT NOT NULL,
  url             TEXT NOT NULL,
  published_at    TEXT NOT NULL,
  fact_label      TEXT NOT NULL CHECK (fact_label IN (
                    'Proven','Established','Alleged','Disputed','Not established'
                  )),
  steelman_for    TEXT NOT NULL,
  steelman_against TEXT NOT NULL,
  evidence_notes  TEXT,
  weight          REAL NOT NULL,
  signed_score    REAL,                       -- NULL when accountability_exempt
  methodology_version TEXT NOT NULL DEFAULT '0.1-draft',
  coder           TEXT,
  credit          TEXT,
  target_inferred INTEGER NOT NULL DEFAULT 0,  -- 1 if AfriMAGA/etc. mapped to org via context
  target_context_quote TEXT,                  -- required when target_inferred=1
  sample_frame    TEXT CHECK (sample_frame IS NULL OR sample_frame IN
                    ('keyword','neutral_random','counter_pull','external_seed','purposive')),
  accountability_status TEXT CHECK (accountability_status IS NULL OR accountability_status IN
                    ('bias','borderline','accountability_exempt','accountability','neutral_method','control')),
  published_at_precision TEXT CHECK (published_at_precision IS NULL OR published_at_precision IN
                    ('date','datetime')),
  created_at      TEXT NOT NULL,
  CHECK (article_id IS NOT NULL OR public_post_id IS NOT NULL),
  CHECK (target_inferred IN (0,1)),
  CHECK (target_inferred = 0 OR (target_context_quote IS NOT NULL AND length(target_context_quote) > 0)),
  CHECK (signed_score IS NULL OR (signed_score BETWEEN -2 AND 2))
);

CREATE TABLE score_runs (
  id              TEXT PRIMARY KEY,
  methodology_version TEXT NOT NULL,
  run_at          TEXT NOT NULL,
  notes           TEXT
);

CREATE TABLE scores (
  id              TEXT PRIMARY KEY,
  score_run_id    TEXT NOT NULL REFERENCES score_runs(id),
  level           TEXT NOT NULL CHECK (level IN ('article','person','publication')),
  subject_id      TEXT NOT NULL,              -- article_id | person_id | publication_id
  actor           TEXT NOT NULL,
  score           REAL NOT NULL,              -- −2..+2
  n_findings      INTEGER NOT NULL,
  confidence      TEXT CHECK (confidence IN ('low','medium','high')),
  display         TEXT CHECK (display IN ('hidden','provisional','full'))
);

CREATE INDEX idx_findings_pub_actor ON findings(publication_id, actor);
CREATE INDEX idx_findings_person_actor ON findings(person_id, actor);
CREATE INDEX idx_articles_pub ON articles(publication_id);
CREATE INDEX idx_posts_person ON public_posts(person_id);

-- Secondary meter (left/right lean) — NEVER mix with primary `scores`
CREATE TABLE lean_score_runs (
  id              TEXT PRIMARY KEY,
  left_right_method_version TEXT NOT NULL DEFAULT '0.1-draft',
  actor_axis_map_hash TEXT,                   -- hash/version of data/actor_axis_map.csv
  run_at          TEXT NOT NULL,
  notes           TEXT,
  draft           INTEGER NOT NULL DEFAULT 1 CHECK (draft IN (0,1))
);

CREATE TABLE lean_scores (
  id              TEXT PRIMARY KEY,
  lean_score_run_id TEXT NOT NULL REFERENCES lean_score_runs(id),
  entity_type     TEXT NOT NULL CHECK (entity_type IN ('publication','person')),
  entity_id       TEXT NOT NULL,              -- publication_id | person_id
  sample_frame    TEXT,                       -- NULL = pooled; else keyword|neutral_random|counter_pull|external_seed|purposive
  lean_economic   REAL,                       -- −2..+2; NULL when findings_only (not stored-and-hidden)
  lean_social     REAL,                       -- NULL when findings_only
  lean_composite  REAL,                       -- NULL when findings_only
  n_included      INTEGER NOT NULL,
  n_skipped       INTEGER NOT NULL DEFAULT 0,
  flag            TEXT NOT NULL CHECK (flag IN ('findings_only','provisional','full')),
  share_contested_placements REAL,
  secondary_view_banner TEXT NOT NULL DEFAULT
    'Secondary view: left/right lean (reader convenience). The primary measure is for/against named actors.',
  caveat          TEXT NOT NULL DEFAULT
    'The left/right split is contested in South Africa.',
  direct_lean_label_signals_json TEXT,        -- optional documented signals; not folded into lean_* by default
  CHECK (lean_economic IS NULL OR (lean_economic BETWEEN -2 AND 2)),
  CHECK (lean_social IS NULL OR (lean_social BETWEEN -2 AND 2)),
  CHECK (lean_composite IS NULL OR (lean_composite BETWEEN -2 AND 2)),
  CHECK (flag != 'findings_only' OR (
           lean_economic IS NULL AND lean_social IS NULL AND lean_composite IS NULL))
);

CREATE TABLE actor_axis_map (
  actor           TEXT PRIMARY KEY,
  economic_axis   REAL,                       -- NULL = unmapped / excluded
  social_axis     REAL,
  placement_contested TEXT NOT NULL CHECK (placement_contested IN ('no','partial','yes','n/a')),
  rationale       TEXT NOT NULL,
  sources         TEXT NOT NULL,
  CHECK (economic_axis IS NULL OR (economic_axis BETWEEN -2 AND 2)),
  CHECK (social_axis IS NULL OR (social_axis BETWEEN -2 AND 2))
);

CREATE INDEX idx_lean_scores_entity ON lean_scores(entity_type, entity_id);

