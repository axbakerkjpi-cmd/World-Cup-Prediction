# GitHub Release Checklist

## First publish

```powershell
git init
git add .
git commit -m "Create SFM 1.0 prototype"
git branch -M main
git remote add origin https://github.com/YOUR_NAME/serenity-football-model.git
git push -u origin main
```

## Local install

```powershell
py -3.9 -m pip install -e .
sfm predict
sfm update
```

## Data update workflow

1. Edit `config/data_sources.json`.
2. Keep sample `local_csv` sources enabled for local testing.
3. Enable real API sources such as `football_data_org_matches` and
   `the_odds_api_h2h` when API keys are available.
4. Put API keys in environment variables, never in Git.

Example HTTP source:

```json
{
  "name": "external_matches",
  "type": "http_csv",
  "url": "https://example.com/matches.csv",
  "target": "matches.csv",
  "api_key_env": "SFM_API_KEY",
  "api_key_header": "X-Auth-Token"
}
```

Run:

```powershell
sfm update --output-dir data/live
sfm predict --data-dir data/live
```
