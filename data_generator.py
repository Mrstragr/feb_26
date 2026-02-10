from __future__ import annotations

from datetime import datetime
import random
from typing import Dict, List


Transaction = Dict[str, object]


def generate_sample_transactions(months: int = 6, seed: int = 42, stress_profile: str = "medium") -> List[Transaction]:
    random.seed(seed)
    today = datetime.now()

    profile_map = {
        "low": {"expense_boost": 0.82, "income_vol": 0.04, "overdraft_prob": 0.01},
        "medium": {"expense_boost": 0.95, "income_vol": 0.10, "overdraft_prob": 0.06},
        "high": {"expense_boost": 1.10, "income_vol": 0.22, "overdraft_prob": 0.20},
    }
    profile = profile_map.get(stress_profile.lower(), profile_map["medium"])

    rows: List[Transaction] = []
    for m in range(months):
        month = ((today.month - months + m - 1) % 12) + 1
        year = today.year + ((today.month - months + m - 1) // 12)

        income = max(1500.0, random.gauss(3500.0, 3500.0 * profile["income_vol"]))
        rows.append({
            "date": f"{year:04d}-{month:02d}-02",
            "type": "income",
            "category": "salary",
            "amount": round(income, 2),
            "overdraft": 0,
        })

        essentials = {"rent": 1200.0, "groceries": 350.0, "utilities": 180.0, "transport": 150.0}
        spike_factor = 1 + (0.05 * m if stress_profile.lower() == "high" else 0.0)

        for category, base in essentials.items():
            amount = max(20.0, random.gauss(base * profile["expense_boost"] * spike_factor, base * 0.08))
            rows.append({
                "date": f"{year:04d}-{month:02d}-{random.randint(3, 24):02d}",
                "type": "expense",
                "category": category,
                "amount": round(amount, 2),
                "overdraft": 1 if random.random() < profile["overdraft_prob"] else 0,
            })

        discretionary = ["dining", "shopping", "entertainment", "subscriptions"]
        for _ in range(10):
            amount = max(5.0, random.gauss(85.0 * profile["expense_boost"], 40.0))
            rows.append({
                "date": f"{year:04d}-{month:02d}-{random.randint(1, 27):02d}",
                "type": "expense",
                "category": random.choice(discretionary),
                "amount": round(amount, 2),
                "overdraft": 1 if random.random() < profile["overdraft_prob"] else 0,
            })

    rows.sort(key=lambda x: str(x["date"]))
    return rows
