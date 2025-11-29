# VCT2024-Analysis
Valorant Championship Tour 2024 Analysis

## What’s here
- `scripts/fetch_vct_data.py`: Fetch VCT 2024 data from VLR.gg (via `vlrdevapi`), write CSVs, and optionally load into SQLite.
- `sql/schema.sql`: SQLite table definitions (agent-level rows + match-level rows).
- `sql/example_queries.sql`: Ready-to-run SQL for win-rate, agent pick-rate, and team stats.
- `requirements.txt`: Minimal Python deps.

## Quickstart
1) Install deps (ideally in a venv):
```bash
pip install -r requirements.txt
```

2) Fetch data (needs network):
```bash
python scripts/fetch_vct_data.py --year 2024 \
  --events 50 \
  --out data/vct2024_agent_rounds.csv \
  --matches-out data/vct2024_matches.csv \
  --db data/vct2024.sqlite
```
- `--events` lets you limit events if you just want a sample.
- Omit `--db` if you don’t want a SQLite file.
- If you get a “DataFrames empty” error, it means no rows were fetched (e.g., network/rate-limit or filters too strict). Retry without `--events` or check connectivity.

If you hit import errors with `vlrdevapi`, do a clean reinstall:
```bash
python3 -m pip uninstall -y vlrdevapi vlr
python3 -m pip install --upgrade vlrdevapi
```
The script targets `vlrdevapi` 1.4.x (functions under `vlrdevapi.events` and `vlrdevapi.series`).

If the script logs “Warning: no data fetched”, it means nothing was returned
(possible network/rate-limit or missing dates on events). Retry without `--events`
or rerun after a short wait.

3) Run SQL analyses (SQLite example):
```bash
sqlite3 data/vct2024.sqlite < sql/example_queries.sql
```

4) Build your report from the outputs:
- By region: win-rate, ACS/KD, agent usage.
- By agent: pick-rate and win-rate globally and per region.
- By team: win-rate (filter min maps).

## CSV columns (agent rows)
- event_id, event_name, region, match_id, map, team, player, agent
- kills, deaths, assists, acs, fk, fd, rounds_played, result (1 win / 0 loss)

## CSV columns (match rows)
- event_id, event_name, region, match_id, map, team, opponent, rounds_played, result, start_time

## Notes
- This repo does not ship data; you must run the fetch script with network access.
- The VLR API surface can change; if a field is missing, adjust the mapping in `fetch_vct_data.py`.
- For deeper visuals, load the CSV into pandas/Seaborn and plot (e.g., pick-rate vs win-rate per agent, region win-rate bars).
