# AI-Powered Early Warning System for Financial Stress Detection

Hackathon-ready MVP that detects early warning signs of financial stress using transaction-level behavior patterns.

## ✅ Features
- Financial stress risk score from `0-100`
- Risk band classification: `Low / Medium / High`
- Monthly risk trend output
- Actionable and personalized recommendations
- Synthetic dataset generation for demo mode
- HTML dashboard generator (single-file output)

## 🧠 Core signal engine
The current MVP computes a weighted risk score from:
1. Expense-to-income ratio
2. Income volatility
3. Savings rate
4. Essential spending spikes
5. Overdraft frequency

> This is intentionally interpretable for hackathons. You can later swap this engine with an ML classifier once labeled data is available.

## 🚀 Run locally
```bash
python app.py --months 9 --profile medium --seed 42 --output dashboard.html
```
Then open `dashboard.html` in a browser.

## 🧪 Run tests
```bash
pytest -q
```

## Files
- `stress_model.py`: scoring model + recommendations + monthly trend builder.
- `data_generator.py`: synthetic transaction generator for low/medium/high stress behavior.
- `app.py`: generates a visual dashboard (`dashboard.html`) with risk chart and insights.
- `tests/test_stress_model.py`: core behavioral checks.
