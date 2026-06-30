# SFM 1.0 - Serenity Football Model

SFM is a local football prediction system. The first version focuses on a clear,
auditable prediction engine, configurable data updates, and a package structure
that can be published on GitHub.

## What is included

- Team rating database in CSV form
- Match input database in CSV form
- Elo-adjusted attacking expectation
- Double Poisson score matrix
- Win/draw/loss probabilities
- Simple market value index
- Brier score and log-loss helpers
- Monte Carlo simulation helper
- Local HTML dashboard generator
- Configurable data updater for local CSV, HTTP CSV, football-data.org, and
  The Odds API sources
- Python package metadata and CLI entry point

## Quick start

Use Python 3.9 or newer:

```powershell
py -3.9 scripts/run_demo.py
```

This writes:

- `outputs/predictions.csv`
- `outputs/dashboard.html`

Open `outputs/dashboard.html` in a browser to view the first local dashboard.

## Command line usage

Install the package locally:

```powershell
py -3.9 -m pip install -e .
```

Run predictions:

```powershell
sfm predict
```

Refresh data from configured sources:

```powershell
sfm update
sfm predict --data-dir data/live
```

Data sources are configured in `config/data_sources.json`. The updater supports:

- `local_csv`: copy a controlled CSV into the live data folder
- `http_csv`: download a live CSV endpoint, optionally with an API key from an
  environment variable
- `football_data_org_teams`: download teams from football-data.org
- `football_data_org_matches`: download fixtures/results from football-data.org
- `the_odds_api_h2h`: download 1X2 odds from The Odds API and optionally merge
  them into `matches.csv`

Real API templates are already included in `config/data_sources.json` with
`enabled: false`. Add your API keys as environment variables and switch the
sources you want to `enabled: true`.

```powershell
$env:FOOTBALL_DATA_API_KEY="your-football-data-key"
$env:ODDS_API_KEY="your-odds-api-key"
sfm update
```

See `docs/DATA_SOURCES.md` for the full data-source guide.

## Project layout

```text
data/
  live/
  sample/
    teams.csv
    matches.csv
config/
  data_sources.json
sfm_engine/
  cli.py
  calibration.py
  dashboard.py
  data_io.py
  elo.py
  models.py
  monte_carlo.py
  poisson.py
  predictor.py
  updater.py
scripts/
  run_demo.py
  update_data.py
docs/
  DATA_SOURCES.md
  GITHUB_RELEASE.md
tests/
  test_engine.py
outputs/
```

## Version direction

- SFM 1.0: local probability model for tournament matches
- SFM 1.1: automated data update and odds ingestion
- SFM 1.2: qualification paths, penalties, and deeper simulation
- SFM 2.0: model calibration and machine-learning weight tuning
