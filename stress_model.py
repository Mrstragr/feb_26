from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from statistics import mean, pstdev
from typing import Dict, List, Tuple


Transaction = Dict[str, object]


@dataclass
class StressAssessment:
    score: float
    level: str
    metrics: Dict[str, float]
    recommendations: List[str]


class FinancialStressDetector:
    """Rule-based scoring model for early financial stress detection."""

    def __init__(self) -> None:
        self.weights = {
            "expense_to_income_ratio": 0.3,
            "income_volatility": 0.2,
            "savings_rate": 0.2,
            "essential_spike": 0.15,
            "overdraft_frequency": 0.15,
        }

    @staticmethod
    def _safe_divide(a: float, b: float) -> float:
        return float(a / b) if b else 0.0

    @staticmethod
    def _month_key(date_text: str) -> str:
        return datetime.fromisoformat(date_text).strftime("%Y-%m")

    def compute_features(self, transactions: List[Transaction]) -> Dict[str, float]:
        if not transactions:
            return {
                "expense_to_income_ratio": 0.0,
                "income_volatility": 0.0,
                "savings_rate": 0.0,
                "essential_spike": 0.0,
                "overdraft_frequency": 0.0,
            }

        monthly_income: Dict[str, float] = {}
        monthly_expenses: Dict[str, float] = {}
        essential_monthly: Dict[str, float] = {}
        overdraft_values: List[int] = []

        essential_categories = {"rent", "groceries", "utilities", "transport"}

        for tx in transactions:
            month = self._month_key(str(tx["date"]))
            tx_type = str(tx["type"])
            amount = float(tx["amount"])
            category = str(tx["category"])
            overdraft = int(tx.get("overdraft", 0))

            if tx_type == "income":
                monthly_income[month] = monthly_income.get(month, 0.0) + amount
            elif tx_type == "expense":
                monthly_expenses[month] = monthly_expenses.get(month, 0.0) + amount
                if category in essential_categories:
                    essential_monthly[month] = essential_monthly.get(month, 0.0) + amount

            overdraft_values.append(overdraft)

        incomes = list(monthly_income.values())
        expenses = list(monthly_expenses.values())

        avg_income = mean(incomes) if incomes else 0.0
        avg_expenses = mean(expenses) if expenses else 0.0

        expense_to_income_ratio = min(self._safe_divide(avg_expenses, avg_income), 2.0)
        income_volatility = min(self._safe_divide(pstdev(incomes), avg_income) if len(incomes) > 1 else 0.0, 1.5)
        savings_rate = max(self._safe_divide(avg_income - avg_expenses, avg_income), -1.0) if avg_income else 0.0

        essential_months_sorted = sorted(essential_monthly)
        if len(essential_months_sorted) >= 2:
            latest_month = essential_months_sorted[-1]
            previous_values = [essential_monthly[m] for m in essential_months_sorted[:-1]]
            baseline = mean(previous_values)
            latest = essential_monthly[latest_month]
            essential_spike = max(self._safe_divide(latest - baseline, baseline), 0.0) if baseline else 0.0
        else:
            essential_spike = 0.0
        essential_spike = min(essential_spike, 1.5)

        overdraft_frequency = self._safe_divide(sum(overdraft_values), len(overdraft_values)) if overdraft_values else 0.0
        overdraft_frequency = min(max(overdraft_frequency, 0.0), 1.0)

        return {
            "expense_to_income_ratio": expense_to_income_ratio,
            "income_volatility": income_volatility,
            "savings_rate": savings_rate,
            "essential_spike": essential_spike,
            "overdraft_frequency": overdraft_frequency,
        }

    def _normalize_feature(self, name: str, value: float) -> float:
        if name == "expense_to_income_ratio":
            return min(value / 1.2, 1.0)
        if name == "income_volatility":
            return min(value / 0.5, 1.0)
        if name == "savings_rate":
            if value >= 0.2:
                return 0.0
            if value >= 0:
                return (0.2 - value) / 0.2 * 0.6
            return min(0.6 + min(abs(value) / 0.5, 1.0) * 0.4, 1.0)
        if name == "essential_spike":
            return min(value / 0.4, 1.0)
        if name == "overdraft_frequency":
            return value
        return 0.0

    def assess(self, transactions: List[Transaction]) -> StressAssessment:
        metrics = self.compute_features(transactions)
        normalized = {k: self._normalize_feature(k, v) for k, v in metrics.items()}
        score = 100.0 * sum(self.weights[k] * normalized[k] for k in self.weights)

        if score < 35:
            level = "Low"
        elif score < 65:
            level = "Medium"
        else:
            level = "High"

        recommendations = self.generate_recommendations(level, metrics)
        return StressAssessment(score=round(score, 2), level=level, metrics=metrics, recommendations=recommendations)

    def generate_recommendations(self, level: str, metrics: Dict[str, float]) -> List[str]:
        recs = []
        if metrics["expense_to_income_ratio"] > 0.85:
            recs.append("Reduce non-essential spending by setting category-wise weekly limits.")
        if metrics["income_volatility"] > 0.25:
            recs.append("Build a 3-month emergency fund to absorb irregular income periods.")
        if metrics["savings_rate"] < 0.1:
            recs.append("Automate savings transfers on payday, even with a small fixed amount.")
        if metrics["essential_spike"] > 0.2:
            recs.append("Review recent essential bill increases and negotiate or optimize providers.")
        if metrics["overdraft_frequency"] > 0.1:
            recs.append("Set low-balance alerts and keep a small cash buffer to avoid overdrafts.")

        if not recs and level == "Low":
            recs.append("Current trend is stable. Continue monthly reviews and maintain your savings habit.")
        if level == "High":
            recs.append("Consider speaking with a financial counselor for a debt-prioritization plan.")
        return recs


def build_monthly_risk_trend(transactions: List[Transaction]) -> Tuple[List[Dict[str, object]], FinancialStressDetector]:
    detector = FinancialStressDetector()
    if not transactions:
        return [], detector

    months = sorted({datetime.fromisoformat(str(tx["date"])).strftime("%Y-%m") for tx in transactions})
    trend: List[Dict[str, object]] = []

    for month in months:
        partial = [
            tx
            for tx in transactions
            if datetime.fromisoformat(str(tx["date"])).strftime("%Y-%m") <= month
        ]
        assessment = detector.assess(partial)
        trend.append({"month": month, "score": assessment.score, "level": assessment.level})

    return trend, detector
