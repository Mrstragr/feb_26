from __future__ import annotations

import argparse
import json
from pathlib import Path

from data_generator import generate_sample_transactions
from stress_model import build_monthly_risk_trend


def generate_dashboard(months: int, profile: str, seed: int, output: str) -> Path:
    transactions = generate_sample_transactions(months=months, stress_profile=profile, seed=seed)
    trend, detector = build_monthly_risk_trend(transactions)
    latest = detector.assess(transactions)

    months_js = json.dumps([row["month"] for row in trend])
    scores_js = json.dumps([row["score"] for row in trend])
    tx_preview = "\n".join(
        f"<tr><td>{t['date']}</td><td>{t['type']}</td><td>{t['category']}</td><td>{t['amount']}</td><td>{t['overdraft']}</td></tr>"
        for t in transactions[:20]
    )
    recommendations = "\n".join(f"<li>{r}</li>" for r in latest.recommendations)
    metrics = "\n".join(f"<li><b>{k}</b>: {v:.3f}</li>" for k, v in latest.metrics.items())

    html = f"""<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8'>
  <title>Financial Stress Dashboard</title>
  <script src='https://cdn.jsdelivr.net/npm/chart.js'></script>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; background: #f8fafc; color: #0f172a; }}
    .cards {{ display: flex; gap: 16px; margin-bottom: 24px; }}
    .card {{ background: white; padding: 16px; border-radius: 10px; box-shadow: 0 1px 4px rgba(0,0,0,.08); flex: 1; }}
    .section {{ background: white; padding: 16px; border-radius: 10px; box-shadow: 0 1px 4px rgba(0,0,0,.08); margin-bottom: 16px; }}
    table {{ width: 100%; border-collapse: collapse; }}
    td, th {{ border-bottom: 1px solid #e2e8f0; text-align: left; padding: 8px; font-size: 14px; }}
  </style>
</head>
<body>
  <h1>📉 AI Financial Stress Early Warning</h1>
  <p>Scenario: <b>{profile}</b> profile over <b>{months}</b> months.</p>

  <div class='cards'>
    <div class='card'><h3>Stress Score</h3><p>{latest.score}/100</p></div>
    <div class='card'><h3>Risk Level</h3><p>{latest.level}</p></div>
    <div class='card'><h3>Savings Rate</h3><p>{latest.metrics['savings_rate']*100:.1f}%</p></div>
  </div>

  <div class='section'>
    <h2>Risk trend</h2>
    <canvas id='riskChart' height='90'></canvas>
  </div>

  <div class='section'>
    <h2>Current risk drivers</h2>
    <ul>{metrics}</ul>
  </div>

  <div class='section'>
    <h2>Recommendations</h2>
    <ul>{recommendations}</ul>
  </div>

  <div class='section'>
    <h2>Sample transactions</h2>
    <table>
      <thead><tr><th>Date</th><th>Type</th><th>Category</th><th>Amount</th><th>Overdraft</th></tr></thead>
      <tbody>{tx_preview}</tbody>
    </table>
  </div>

  <script>
    const ctx = document.getElementById('riskChart').getContext('2d');
    new Chart(ctx, {{
      type: 'line',
      data: {{
        labels: {months_js},
        datasets: [{{
          label: 'Stress Score',
          data: {scores_js},
          borderColor: '#2563eb',
          tension: 0.2,
          fill: false
        }}]
      }},
      options: {{
        scales: {{ y: {{ suggestedMin: 0, suggestedMax: 100 }} }}
      }}
    }});
  </script>
</body>
</html>
"""

    output_path = Path(output)
    output_path.write_text(html, encoding="utf-8")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a hackathon dashboard HTML for financial stress detection")
    parser.add_argument("--months", type=int, default=9)
    parser.add_argument("--profile", type=str, default="medium", choices=["low", "medium", "high"])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=str, default="dashboard.html")
    args = parser.parse_args()

    file_path = generate_dashboard(months=args.months, profile=args.profile, seed=args.seed, output=args.output)
    print(f"Dashboard generated at: {file_path}")
