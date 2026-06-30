# Data Sources

SFM separates model logic from data collection. Configure sources once in
`config/data_sources.json`, then run:

```powershell
sfm update
sfm predict --data-dir data\live
```

## Source Types

`local_csv` copies a local CSV into `data/live`. This is useful for controlled
research datasets and manual overrides.

`http_csv` downloads a CSV file from an HTTP endpoint.

`football_data_org_teams` downloads teams from football-data.org and writes
`teams.csv`.

`football_data_org_matches` downloads fixtures/results from football-data.org
and writes `matches.csv`.

`the_odds_api_h2h` downloads 1X2 odds from The Odds API and writes `odds.csv`.
If `merge_matches_target` is set, it also fills the odds columns in
`matches.csv` when date, home team, and away team match.

## Enable Real APIs

Real API templates are already included in `config/data_sources.json` with
`enabled: false`. Change the ones you want to `enabled: true`.

Keep keys out of Git. Set them in PowerShell:

```powershell
$env:FOOTBALL_DATA_API_KEY="your-football-data-key"
$env:ODDS_API_KEY="your-odds-api-key"
sfm update
```

## football-data.org Example

```json
{
  "name": "world_cup_matches",
  "enabled": true,
  "type": "football_data_org_matches",
  "competition": "WC",
  "season": "2026",
  "target": "matches.csv",
  "neutral_site": "true",
  "api_key_env": "FOOTBALL_DATA_API_KEY"
}
```

## The Odds API Example

```json
{
  "name": "world_cup_odds",
  "enabled": true,
  "type": "the_odds_api_h2h",
  "sport": "soccer_fifa_world_cup",
  "regions": "us,uk,eu",
  "markets": "h2h",
  "target": "odds.csv",
  "merge_matches_target": "matches.csv",
  "api_key_env": "ODDS_API_KEY"
}
```

## Practical Notes

- Schedules and teams can be automated with football-data.org.
- Odds can be automated with The Odds API.
- xG, injuries, and expected lineups usually require paid or specialist data.
- Elo can be imported from a provider later, but SFM can also compute its own Elo
  from historical results in a future module.
