"""
Fetch VCT 2024 data from VLR.gg using vlrdevapi (v1.4.x API surface),
save CSVs, and optionally load them into a SQLite database.

Outputs:
- Agent-level rows: one row per player per map with agent + performance stats.
- Match-level rows: one row per team per map with win/loss + rounds.

Example:
python scripts/fetch_vct_data.py --year 2024 \
  --events 50 \
  --out data/vct2024_agent_rounds.csv \
  --matches-out data/vct2024_matches.csv \
  --db data/vct2024.sqlite

Notes:
- This script does not run inside this environment (no network). Run locally.
- Targets vlrdevapi 1.4.x (functions exposed under vlrdevapi.events/series).
"""
from __future__ import annotations

import argparse
import os
import sqlite3
from typing import Dict, List, Any

import pandas as pd
from vlrdevapi import events, series
from vlrdevapi.events import EventTier, EventStatus


def fetch_events_for_year(year: int, limit_events: int | None):
    """List VCT events and filter by start_date year."""
    evs = events.list_events(
        tier=EventTier.VCT,
        status=EventStatus.ALL,
        limit=limit_events or None,
    )
    filtered = []
    for ev in evs:
        sd, ed = ev.start_date, ev.end_date
        if (sd and sd.year == year) or (ed and ed.year == year):
            filtered.append(ev)
        elif sd is None and ed is None:
            # If dates are missing, keep it (fallback) so we don't drop valid events.
            filtered.append(ev)
    # If everything got filtered out, fallback to the raw list (better to fetch something than nothing)
    return filtered or evs


def fetch_rows_for_events(evs) -> tuple[pd.DataFrame, pd.DataFrame]:
    agent_rows = []
    match_rows = []

    for ev in evs:
        eid = ev.id
        region = ev.region
        event_name = ev.name
        ev_matches = events.matches(event_id=eid, limit=None)

        for m in ev_matches:
            mid = m.match_id
            map_stats = series.matches(series_id=mid, limit=None)

            for mp in map_stats:
                map_name = mp.map_name
                teams = mp.teams or ()
                if len(teams) != 2:
                    continue
                t1, t2 = teams

                # Build match rows (team-level)
                for team_obj, opp_obj in ((t1, t2), (t2, t1)):
                    match_rows.append(
                        {
                            "event_id": eid,
                            "event_name": event_name,
                            "region": region,
                            "match_id": mid,
                            "map": map_name,
                            "team": team_obj.name,
                            "opponent": opp_obj.name,
                            "rounds_played": (team_obj.score or 0) + (opp_obj.score or 0),
                            "result": 1 if team_obj.is_winner else 0,
                            "start_time": None,  # not available in this API surface
                        }
                    )

                # Build agent/player rows
                for p in mp.players:
                    agent_rows.append(
                        {
                            "event_id": eid,
                            "event_name": event_name,
                            "region": region,
                            "match_id": mid,
                            "map": map_name,
                            "team": p.team_short,
                            "player": p.name,
                            "agent": p.agents[0] if p.agents else None,
                            "kills": p.k,
                            "deaths": p.d,
                            "assists": p.a,
                            "acs": p.acs,
                            "fk": p.fk,
                            "fd": p.fd,
                            "rounds_played": (t1.score or 0) + (t2.score or 0),
                            "result": 1 if (t1.is_winner and p.team_short == t1.short) or (t2.is_winner and p.team_short == t2.short) else 0,
                        }
                    )

    return pd.DataFrame(agent_rows), pd.DataFrame(match_rows)


def ensure_parents(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


def write_sqlite(
    df_agents: pd.DataFrame, df_matches: pd.DataFrame, db_path: str
) -> None:
    if df_agents.empty or df_matches.empty:
        print("Warning: no data fetched; skipping SQLite write.")
        return
    ensure_parents(db_path)
    conn = sqlite3.connect(db_path)
    try:
        df_agents.to_sql("agent_rounds", conn, if_exists="replace", index=False)
        df_matches.to_sql("matches", conn, if_exists="replace", index=False)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_region ON agent_rounds(region)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_match ON agent_rounds(match_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_matches_region ON matches(region)")
        conn.commit()
    finally:
        conn.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch VCT 2024 data from VLR.gg")
    parser.add_argument("--year", type=int, default=2024, help="Season year to fetch")
    parser.add_argument("--events", type=int, default=None, help="Limit number of events (after year filter)")
    parser.add_argument("--out", type=str, default="data/vct2024_agent_rounds.csv", help="Agent rows CSV path")
    parser.add_argument("--matches-out", type=str, default="data/vct2024_matches.csv", help="Match rows CSV path")
    parser.add_argument("--db", type=str, default=None, help="Optional SQLite path to write tables")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    evs = fetch_events_for_year(year=args.year, limit_events=args.events)
    df_agents, df_matches = fetch_rows_for_events(evs)

    ensure_parents(args.out)
    ensure_parents(args.matches_out)
    df_agents.to_csv(args.out, index=False)
    df_matches.to_csv(args.matches_out, index=False)

    if args.db:
        write_sqlite(df_agents, df_matches, args.db)

    print(f"Events fetched: {len(evs)}")
    print(f"Agent rows: {len(df_agents)}, Match rows: {len(df_matches)}")
    print(f"CSV written: {args.out}, {args.matches_out}")
    if args.db:
        print(f"SQLite written: {args.db}")


if __name__ == "__main__":
    main()
