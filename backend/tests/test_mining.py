import pandas as pd
from healthtrend.mining import analyze_monthly


def test_trend_and_mining_outputs_are_real_data_derived():
    frame = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=24, freq="MS"),
        "cases": [100, 110, 120, 130, 125, 140, 150, 160, 155, 170, 180, 190,
                  200, 210, 220, 230, 225, 240, 250, 260, 255, 270, 280, 290],
    })
    results = analyze_monthly(frame)
    types = {r["analysis_type"] for r in results}
    assert {"trend_analysis", "anomaly_screening", "pattern_clustering", "seasonal_decomposition"} <= types
    trend = next(r for r in results if r["analysis_type"] == "trend_analysis")
    assert trend["result"]["slope_per_month"] > 0
    assert trend["sample_size"] == 24


def test_short_series_does_not_fake_seasonal_or_cluster_results():
    frame = pd.DataFrame({"date": pd.date_range("2025-01-01", periods=6, freq="MS"), "cases": [2, 3, 5, 4, 6, 7]})
    results = analyze_monthly(frame)
    assert all(r.get("status") == "insufficient_data" for r in results if r["analysis_type"] in {"pattern_clustering", "seasonal_decomposition"})


def test_analysis_results_have_stable_idempotency_key_fields():
    frame = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=12, freq="MS"),
        "cases": list(range(100, 112)),
    })
    results = analyze_monthly(frame)
    for result in results:
        assert result["analysis_type"]
        assert result["algorithm"]
        assert result["period_start"] == "2024-01-01"
        assert result["period_end"] == "2024-12-01"
