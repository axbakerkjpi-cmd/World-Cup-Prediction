from html import escape
from pathlib import Path
from typing import Iterable, List

from .models import PredictionResult


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def _num(value):
    return "" if value is None else f"{value:.3f}"


def _best_value(prediction: PredictionResult):
    values = {
        prediction.home_team: prediction.value_home,
        "Draw": prediction.value_draw,
        prediction.away_team: prediction.value_away,
    }
    label, value = max(values.items(), key=lambda item: -999 if item[1] is None else item[1])
    return label, value


def render_dashboard(predictions: Iterable[PredictionResult]) -> str:
    rows: List[str] = []
    cards: List[str] = []

    for prediction in predictions:
        label, value = _best_value(prediction)
        rows.append(
            "<tr>"
            f"<td>{escape(prediction.match_id)}</td>"
            f"<td>{escape(prediction.date)}</td>"
            f"<td>{escape(prediction.home_team)} vs {escape(prediction.away_team)}</td>"
            f"<td>{prediction.home_lambda:.2f} - {prediction.away_lambda:.2f}</td>"
            f"<td>{_pct(prediction.home_win_prob)}</td>"
            f"<td>{_pct(prediction.draw_prob)}</td>"
            f"<td>{_pct(prediction.away_win_prob)}</td>"
            f"<td>{escape(prediction.most_likely_score)}</td>"
            f"<td>{escape(label)} ({_num(value)})</td>"
            "</tr>"
        )
        cards.append(
            "<section class='match'>"
            f"<p class='date'>{escape(prediction.date)}</p>"
            f"<h2>{escape(prediction.home_team)} vs {escape(prediction.away_team)}</h2>"
            "<div class='bars'>"
            f"<span style='width:{prediction.home_win_prob * 100:.1f}%'>{escape(prediction.home_team)} {_pct(prediction.home_win_prob)}</span>"
            f"<span style='width:{prediction.draw_prob * 100:.1f}%'>Draw {_pct(prediction.draw_prob)}</span>"
            f"<span style='width:{prediction.away_win_prob * 100:.1f}%'>{escape(prediction.away_team)} {_pct(prediction.away_win_prob)}</span>"
            "</div>"
            f"<p>Most likely score: <strong>{escape(prediction.most_likely_score)}</strong></p>"
            "</section>"
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SFM 1.0 Dashboard</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #17202a;
      --muted: #5f6c7b;
      --line: #d8dee8;
      --home: #1f7a8c;
      --draw: #6c757d;
      --away: #b23a48;
      --bg: #f5f7fa;
      --panel: #ffffff;
    }}
    body {{
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      color: var(--ink);
      background: var(--bg);
    }}
    header {{
      padding: 28px 36px 18px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }}
    h1 {{
      margin: 0;
      font-size: 30px;
      letter-spacing: 0;
    }}
    .subtitle {{
      margin: 8px 0 0;
      color: var(--muted);
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 24px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }}
    .match {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
    }}
    .date {{
      margin: 0 0 8px;
      color: var(--muted);
      font-size: 13px;
    }}
    .match h2 {{
      font-size: 17px;
      margin: 0 0 14px;
    }}
    .bars {{
      display: grid;
      gap: 8px;
    }}
    .bars span {{
      display: block;
      min-width: 92px;
      box-sizing: border-box;
      padding: 8px 10px;
      border-radius: 4px;
      color: #fff;
      font-size: 13px;
      white-space: nowrap;
    }}
    .bars span:nth-child(1) {{ background: var(--home); }}
    .bars span:nth-child(2) {{ background: var(--draw); }}
    .bars span:nth-child(3) {{ background: var(--away); }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
    }}
    th, td {{
      text-align: left;
      padding: 11px 12px;
      border-bottom: 1px solid var(--line);
      font-size: 14px;
    }}
    th {{
      background: #eef2f6;
      color: #344054;
    }}
    tr:last-child td {{
      border-bottom: 0;
    }}
  </style>
</head>
<body>
  <header>
    <h1>SFM 1.0 Dashboard</h1>
    <p class="subtitle">Serenity Football Model local probability prototype</p>
  </header>
  <main>
    <div class="grid">
      {''.join(cards)}
    </div>
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Date</th>
          <th>Match</th>
          <th>xG lambda</th>
          <th>Home</th>
          <th>Draw</th>
          <th>Away</th>
          <th>Top score</th>
          <th>Best value</th>
        </tr>
      </thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
  </main>
</body>
</html>"""


def write_dashboard(path: Path, predictions: Iterable[PredictionResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_dashboard(predictions), encoding="utf-8")
