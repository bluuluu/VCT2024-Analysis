-- Basic schema for SQLite. Tables will be overwritten by the script.
DROP TABLE IF EXISTS agent_rounds;
DROP TABLE IF EXISTS matches;

CREATE TABLE agent_rounds (
  event_id TEXT,
  event_name TEXT,
  region TEXT,
  match_id TEXT,
  map TEXT,
  team TEXT,
  player TEXT,
  agent TEXT,
  kills INTEGER,
  deaths INTEGER,
  assists INTEGER,
  acs REAL,
  fk INTEGER,
  fd INTEGER,
  rounds_played INTEGER,
  result INTEGER -- 1 = win, 0 = loss
);

CREATE TABLE matches (
  event_id TEXT,
  event_name TEXT,
  region TEXT,
  match_id TEXT,
  map TEXT,
  team TEXT,
  opponent TEXT,
  rounds_played INTEGER,
  result INTEGER, -- 1 = win, 0 = loss
  start_time TEXT
);

CREATE INDEX idx_agent_region ON agent_rounds(region);
CREATE INDEX idx_agent_match ON agent_rounds(match_id);
CREATE INDEX idx_matches_region ON matches(region);
