import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class DataUpdateError(RuntimeError):
    pass


def _resolve_local_path(raw_path: str, config_path: Path) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path

    config_relative = config_path.parent / path
    if config_relative.exists():
        return config_relative

    project_relative = config_path.parent.parent / path
    return project_relative


def _copy_local_csv(source: Dict[str, str], output_dir: Path, config_path: Path) -> Path:
    from_path = _resolve_local_path(source["path"], config_path)
    to_path = output_dir / source["target"]
    to_path.parent.mkdir(parents=True, exist_ok=True)
    if from_path.resolve() != to_path.resolve():
        shutil.copyfile(from_path, to_path)
    return to_path


def _headers(source: Dict[str, str]) -> Dict[str, str]:
    headers = {"User-Agent": "SFM/1.0"}
    if source.get("api_key_env"):
        import os

        api_key = os.environ.get(source["api_key_env"])
        if not api_key:
            raise DataUpdateError(f"Missing environment variable: {source['api_key_env']}")
        headers[source.get("api_key_header", "X-Auth-Token")] = api_key
    return headers


def _download_bytes(source: Dict[str, str], url: str) -> bytes:
    request = Request(url, headers=_headers(source))
    with urlopen(request, timeout=int(source.get("timeout_seconds", 20))) as response:
        return response.read()


def _download_csv(source: Dict[str, str], output_dir: Path) -> Path:
    to_path = output_dir / source["target"]
    to_path.parent.mkdir(parents=True, exist_ok=True)
    to_path.write_bytes(_download_bytes(source, source["url"]))
    return to_path


def _download_json(source: Dict[str, str], url: str) -> Dict:
    return json.loads(_download_bytes(source, url).decode("utf-8"))


def _url_with_query(base_url: str, params: Dict[str, Optional[str]]) -> str:
    clean = {key: value for key, value in params.items() if value not in (None, "")}
    if not clean:
        return base_url
    separator = "&" if "?" in base_url else "?"
    return f"{base_url}{separator}{urlencode(clean)}"


def _write_csv(path: Path, fields: List[str], rows: Iterable[Dict[str, object]]) -> Path:
    import csv

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})
    return path


def _date_from_iso(value: str) -> str:
    if not value:
        return ""
    return value.split("T", 1)[0]


def _football_data_url(source: Dict[str, str], endpoint: str) -> str:
    competition = source["competition"]
    base_url = source.get("base_url", "https://api.football-data.org/v4")
    return f"{base_url}/competitions/{competition}/{endpoint}"


def _football_data_matches(source: Dict[str, str], output_dir: Path) -> Path:
    url = _url_with_query(
        _football_data_url(source, "matches"),
        {
            "season": source.get("season"),
            "dateFrom": source.get("date_from"),
            "dateTo": source.get("date_to"),
            "status": source.get("status"),
            "matchday": source.get("matchday"),
        },
    )
    payload = _download_json(source, url)
    neutral_site = source.get("neutral_site", "true")
    rows = []
    for match in payload.get("matches", []):
        rows.append(
            {
                "match_id": match.get("id", ""),
                "date": _date_from_iso(match.get("utcDate", "")),
                "home_team": match.get("homeTeam", {}).get("name", ""),
                "away_team": match.get("awayTeam", {}).get("name", ""),
                "neutral_site": neutral_site,
                "home_odds": "",
                "draw_odds": "",
                "away_odds": "",
            }
        )

    return _write_csv(
        output_dir / source.get("target", "matches.csv"),
        ["match_id", "date", "home_team", "away_team", "neutral_site", "home_odds", "draw_odds", "away_odds"],
        rows,
    )


def _football_data_teams(source: Dict[str, str], output_dir: Path) -> Path:
    url = _football_data_url(source, "teams")
    payload = _download_json(source, url)
    defaults = {
        "elo": source.get("default_elo", 1500),
        "attack_strength": source.get("default_attack_strength", 1.0),
        "defense_weakness": source.get("default_defense_weakness", 1.0),
        "keeper_strength": source.get("default_keeper_strength", 1.0),
        "penalty_strength": source.get("default_penalty_strength", 1.0),
        "momentum": source.get("default_momentum", 0.0),
    }
    rows = []
    for team in payload.get("teams", []):
        rows.append({"team": team.get("name", ""), **defaults})

    return _write_csv(
        output_dir / source.get("target", "teams.csv"),
        ["team", "elo", "attack_strength", "defense_weakness", "keeper_strength", "penalty_strength", "momentum"],
        rows,
    )


def _best_decimal_prices(bookmakers: List[Dict]) -> Dict[str, float]:
    prices: Dict[str, float] = {}
    for bookmaker in bookmakers:
        for market in bookmaker.get("markets", []):
            if market.get("key") != "h2h":
                continue
            for outcome in market.get("outcomes", []):
                name = outcome.get("name")
                price = outcome.get("price")
                if name and isinstance(price, (int, float)):
                    prices[name] = max(float(price), prices.get(name, 0.0))
    return prices


def _read_csv_dicts(path: Path) -> List[Dict[str, str]]:
    import csv

    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _merge_odds_into_matches(matches_path: Path, odds_rows: List[Dict[str, object]]) -> Optional[Path]:
    if not matches_path.exists():
        return None

    matches = _read_csv_dicts(matches_path)
    odds_by_key = {
        (str(row.get("date")), str(row.get("home_team")), str(row.get("away_team"))): row
        for row in odds_rows
    }
    for match in matches:
        key = (match.get("date", ""), match.get("home_team", ""), match.get("away_team", ""))
        odds = odds_by_key.get(key)
        if not odds:
            continue
        match["home_odds"] = odds.get("home_odds", "")
        match["draw_odds"] = odds.get("draw_odds", "")
        match["away_odds"] = odds.get("away_odds", "")

    _write_csv(
        matches_path,
        ["match_id", "date", "home_team", "away_team", "neutral_site", "home_odds", "draw_odds", "away_odds"],
        matches,
    )
    return matches_path


def _the_odds_api_h2h(source: Dict[str, str], output_dir: Path) -> Path:
    import os

    api_key_env = source.get("api_key_env", "ODDS_API_KEY")
    api_key = os.environ.get(api_key_env)
    if not api_key:
        raise DataUpdateError(f"Missing environment variable: {api_key_env}")

    sport = source.get("sport", "soccer")
    base_url = source.get("base_url", "https://api.the-odds-api.com/v4")
    url = _url_with_query(
        f"{base_url}/sports/{sport}/odds",
        {
            "apiKey": api_key,
            "regions": source.get("regions", "us,uk,eu"),
            "markets": source.get("markets", "h2h"),
            "oddsFormat": source.get("odds_format", "decimal"),
            "dateFormat": source.get("date_format", "iso"),
        },
    )
    payload = _download_json({key: value for key, value in source.items() if key != "api_key_env"}, url)
    rows = []
    for event in payload:
        home_team = event.get("home_team", "")
        away_team = event.get("away_team", "")
        prices = _best_decimal_prices(event.get("bookmakers", []))
        rows.append(
            {
                "match_id": event.get("id", ""),
                "date": _date_from_iso(event.get("commence_time", "")),
                "home_team": home_team,
                "away_team": away_team,
                "home_odds": prices.get(home_team, ""),
                "draw_odds": prices.get("Draw", ""),
                "away_odds": prices.get(away_team, ""),
                "bookmaker_count": len(event.get("bookmakers", [])),
                "source_event_id": event.get("id", ""),
                "updated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            }
        )

    target = _write_csv(
        output_dir / source.get("target", "odds.csv"),
        [
            "match_id",
            "date",
            "home_team",
            "away_team",
            "home_odds",
            "draw_odds",
            "away_odds",
            "bookmaker_count",
            "source_event_id",
            "updated_at",
        ],
        rows,
    )

    merge_target = source.get("merge_matches_target")
    if merge_target:
        _merge_odds_into_matches(output_dir / merge_target, rows)

    return target


def update_from_config(config_path: Path, output_dir: Path) -> List[Path]:
    if not config_path.exists():
        raise DataUpdateError(f"Data source config not found: {config_path}")

    config_path = config_path.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)

    updated: List[Path] = []
    for source in config.get("sources", []):
        if source.get("enabled", True) is False:
            continue
        source_type = source.get("type")
        if source_type == "local_csv":
            updated.append(_copy_local_csv(source, output_dir, config_path))
        elif source_type == "http_csv":
            updated.append(_download_csv(source, output_dir))
        elif source_type == "football_data_org_matches":
            updated.append(_football_data_matches(source, output_dir))
        elif source_type == "football_data_org_teams":
            updated.append(_football_data_teams(source, output_dir))
        elif source_type == "the_odds_api_h2h":
            updated.append(_the_odds_api_h2h(source, output_dir))
        else:
            raise DataUpdateError(f"Unsupported data source type: {source_type}")

    return updated
