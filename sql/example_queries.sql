-- Win rate by region (team-side)
SELECT region, AVG(result) AS win_rate, COUNT(*) AS maps_played
FROM matches
GROUP BY region
ORDER BY win_rate DESC;

-- Agent pick rate by region
WITH counts AS (
  SELECT region, agent, COUNT(*) AS picks
  FROM agent_rounds
  GROUP BY region, agent
),
totals AS (
  SELECT region, SUM(picks) AS total_picks
  FROM counts
  GROUP BY region
)
SELECT c.region, c.agent,
       ROUND(100.0 * c.picks / t.total_picks, 2) AS pick_rate_pct,
       c.picks
FROM counts c
JOIN totals t ON t.region = c.region
ORDER BY c.region, pick_rate_pct DESC;

-- Agent win rate by region (only if agent played >= 50 maps in region)
WITH stats AS (
  SELECT region, agent, AVG(result) AS win_rate, COUNT(*) AS n
  FROM agent_rounds
  GROUP BY region, agent
)
SELECT region, agent, ROUND(win_rate, 3) AS win_rate, n
FROM stats
WHERE n >= 50
ORDER BY region, win_rate DESC;

-- Top teams by win rate (minimum 20 maps)
WITH stats AS (
  SELECT team, region, AVG(result) AS win_rate, COUNT(*) AS maps_played
  FROM matches
  GROUP BY team, region
)
SELECT region, team, ROUND(win_rate, 3) AS win_rate, maps_played
FROM stats
WHERE maps_played >= 20
ORDER BY win_rate DESC;

-- Pick vs win-rate for agents globally (min 200 appearances)
WITH agg AS (
  SELECT agent, AVG(result) AS win_rate, COUNT(*) AS n
  FROM agent_rounds
  GROUP BY agent
)
SELECT agent, ROUND(win_rate, 3) AS win_rate, n
FROM agg
WHERE n >= 200
ORDER BY win_rate DESC;
