import argparse
from pathlib import Path

from .dashboard import write_dashboard
from .data_io import read_matches, read_teams, write_predictions
from .predictor import predict_match
from .updater import update_from_config


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = ROOT / "data" / "sample"
DEFAULT_LIVE_DATA_DIR = ROOT / "data" / "live"
DEFAULT_OUTPUT_DIR = ROOT / "outputs"
DEFAULT_SOURCE_CONFIG = ROOT / "config" / "data_sources.json"


def run_prediction(data_dir: Path = DEFAULT_DATA_DIR, output_dir: Path = DEFAULT_OUTPUT_DIR) -> None:
    teams = read_teams(data_dir / "teams.csv")
    matches = read_matches(data_dir / "matches.csv")
    predictions = [
        predict_match(match, teams[match.home_team], teams[match.away_team])
        for match in matches
    ]

    output_dir.mkdir(parents=True, exist_ok=True)
    write_predictions(output_dir / "predictions.csv", predictions)
    write_dashboard(output_dir / "dashboard.html", predictions)

    print(f"Wrote {output_dir / 'predictions.csv'}")
    print(f"Wrote {output_dir / 'dashboard.html'}")


def run_demo() -> None:
    run_prediction()


def run_update(config_path: Path = DEFAULT_SOURCE_CONFIG, output_dir: Path = DEFAULT_LIVE_DATA_DIR) -> None:
    updated = update_from_config(config_path, output_dir)
    for item in updated:
        print(f"Updated {item}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="sfm", description="Serenity Football Model")
    subparsers = parser.add_subparsers(dest="command", required=True)

    predict_parser = subparsers.add_parser("predict", help="Run predictions and write outputs")
    predict_parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    predict_parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)

    update_parser = subparsers.add_parser("update", help="Refresh local data from configured sources")
    update_parser.add_argument("--config", type=Path, default=DEFAULT_SOURCE_CONFIG)
    update_parser.add_argument("--output-dir", type=Path, default=DEFAULT_LIVE_DATA_DIR)

    args = parser.parse_args()
    if args.command == "predict":
        run_prediction(args.data_dir, args.output_dir)
    elif args.command == "update":
        run_update(args.config, args.output_dir)


if __name__ == "__main__":
    main()
