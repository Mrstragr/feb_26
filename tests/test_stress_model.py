from data_generator import generate_sample_transactions
from stress_model import FinancialStressDetector, build_monthly_risk_trend


def test_assess_returns_valid_range_and_level():
    detector = FinancialStressDetector()
    tx = generate_sample_transactions(months=6, stress_profile="medium")
    result = detector.assess(tx)

    assert 0 <= result.score <= 100
    assert result.level in {"Low", "Medium", "High"}
    assert isinstance(result.recommendations, list)


def test_high_profile_generally_higher_score_than_low_profile():
    detector = FinancialStressDetector()
    low_tx = generate_sample_transactions(months=8, seed=8, stress_profile="low")
    high_tx = generate_sample_transactions(months=8, seed=8, stress_profile="high")

    assert detector.assess(high_tx).score > detector.assess(low_tx).score


def test_trend_has_one_row_per_month():
    tx = generate_sample_transactions(months=7, seed=7, stress_profile="medium")
    trend, _ = build_monthly_risk_trend(tx)

    assert len(trend) == 7
    assert set(trend[0].keys()) == {"month", "score", "level"}


def test_empty_transactions_graceful():
    detector = FinancialStressDetector()
    result = detector.assess([])

    assert result.score == 12.0
    assert result.level == "Low"
