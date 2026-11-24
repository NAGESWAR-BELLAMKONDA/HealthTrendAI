from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from healthtrend.ingestion import validate_monthly_observations


def analyze_monthly(frame: pd.DataFrame) -> list[dict]:
    clean = validate_monthly_observations(frame, "date", "cases")
    if clean.empty:
        raise ValueError("No valid monthly observations to mine")
    dates = pd.to_datetime(clean["date"])
    y = clean["cases"].astype(float).to_numpy()
    month_index = dates.dt.year.to_numpy() * 12 + dates.dt.month.to_numpy()
    x = (month_index - month_index[0]).astype(float)
    expected_months = pd.date_range(dates.iloc[0], dates.iloc[-1], freq='MS')
    is_contiguous = len(expected_months) == len(dates)
    output: list[dict] = []

    if len(y) >= 3:
        slope, intercept = np.polyfit(x, y, 1)
        fitted = slope * x + intercept
        ss_total = float(np.sum((y - y.mean()) ** 2))
        r_squared = 1.0 - float(np.sum((y - fitted) ** 2)) / ss_total if ss_total else None
        output.append({
            "analysis_type": "trend_analysis",
            "algorithm": "ordinary_least_squares_month_index",
            "sample_size": len(y),
            "period_start": dates.iloc[0].date().isoformat(),
            "period_end": dates.iloc[-1].date().isoformat(),
            "result": {
                "slope_per_month": float(slope),
                "intercept": float(intercept),
                "r_squared": r_squared,
                "direction": "increasing" if slope > 0 else "decreasing" if slope < 0 else "flat",
                "mean": float(np.mean(y)),
                "median": float(np.median(y)),
                "standard_deviation": float(np.std(y, ddof=1)) if len(y) > 1 else 0.0,
                "minimum": float(np.min(y)),
                "maximum": float(np.max(y)),
            },
        })

    median = float(np.median(y))
    mad = float(np.median(np.abs(y - median)))
    if len(y) >= 8 and mad > 0:
        robust_z = 0.6745 * (y - median) / mad
        flags = [
            {"date": dates.iloc[i].date().isoformat(), "value": float(y[i]), "robust_z": float(robust_z[i])}
            for i in range(len(y)) if abs(robust_z[i]) >= 3.5
        ]
        output.append({
            "analysis_type": "anomaly_screening",
            "algorithm": "median_absolute_deviation_robust_z",
            "sample_size": len(y),
            "period_start": dates.iloc[0].date().isoformat(),
            "period_end": dates.iloc[-1].date().isoformat(),
            "result": {"threshold": 3.5, "median": median, "mad": mad, "anomalies": flags},
        })
    else:
        output.append({
            "analysis_type": "anomaly_screening",
            "algorithm": "median_absolute_deviation_robust_z",
            "sample_size": len(y),
            "period_start": dates.iloc[0].date().isoformat(),
            "period_end": dates.iloc[-1].date().isoformat(),
            "result": {"message": "Insufficient observations or zero MAD; no anomaly labels assigned."},
            "status": "insufficient_data",
        })

    if len(y) >= 12 and len(np.unique(y)) >= 3:
        month = dates.dt.month.to_numpy()
        features = np.column_stack([
            StandardScaler().fit_transform(y.reshape(-1, 1)).ravel(),
            np.sin(2 * np.pi * month / 12),
            np.cos(2 * np.pi * month / 12),
        ])
        model = KMeans(n_clusters=3, random_state=42, n_init=10)
        labels = model.fit_predict(features)
        clusters = []
        for cluster_id in sorted(np.unique(labels)):
            idx = np.where(labels == cluster_id)[0]
            clusters.append({
                "cluster": int(cluster_id),
                "observations": int(len(idx)),
                "mean_cases": float(np.mean(y[idx])),
                "months": [dates.iloc[i].strftime("%Y-%m") for i in idx],
            })
        output.append({
            "analysis_type": "pattern_clustering",
            "algorithm": "kmeans_k3_standardized_level_and_month_seasonality",
            "sample_size": len(y),
            "period_start": dates.iloc[0].date().isoformat(),
            "period_end": dates.iloc[-1].date().isoformat(),
            "result": {"clusters": clusters, "features": ["standardized_monthly_count", "month_sin", "month_cos"]},
        })
    else:
        output.append({
            "analysis_type": "pattern_clustering",
            "algorithm": "kmeans_k3_standardized_level_and_month_seasonality",
            "sample_size": len(y),
            "period_start": dates.iloc[0].date().isoformat(),
            "period_end": dates.iloc[-1].date().isoformat(),
            "result": {"message": "At least 12 observations and 3 distinct values are required."},
            "status": "insufficient_data",
        })

    if len(y) >= 24 and is_contiguous:
        from statsmodels.tsa.seasonal import STL
        stl = STL(pd.Series(y, index=dates), period=12, robust=True).fit()
        output.append({
            "analysis_type": "seasonal_decomposition",
            "algorithm": "stl_period_12_robust",
            "sample_size": len(y),
            "period_start": dates.iloc[0].date().isoformat(),
            "period_end": dates.iloc[-1].date().isoformat(),
            "result": {
                "trend": [{"date": d.date().isoformat(), "value": float(v)} for d, v in stl.trend.items()],
                "seasonal": [{"date": d.date().isoformat(), "value": float(v)} for d, v in stl.seasonal.items()],
                "residual_std": float(np.std(stl.resid, ddof=1)),
            },
        })
    else:
        output.append({
            "analysis_type": "seasonal_decomposition",
            "algorithm": "stl_period_12_robust",
            "sample_size": len(y),
            "period_start": dates.iloc[0].date().isoformat(),
            "period_end": dates.iloc[-1].date().isoformat(),
            "result": {"message": "At least 24 contiguous monthly observations are required for a 12-month seasonal decomposition; gaps are not interpolated."},
            "status": "insufficient_data",
        })
    return output



def mine_monthly_series(frame: pd.DataFrame) -> list[dict]:
    return analyze_monthly(frame)


def persist(results: list[dict], target: str, location_id: str | None, disease_id: str | None) -> None:
    from supabase import create_client
    client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
    for item in results:
        record = {
            **item,
            "target_name": target,
            "location_id": location_id,
            "disease_id": disease_id,
        }
        client.table("mining_results").upsert(
            record,
            on_conflict="analysis_type,target_name,location_id,disease_id,period_start,period_end,algorithm",
        ).execute()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run descriptive disease-trend mining on verified monthly data.")
    parser.add_argument("--csv", required=True)
    parser.add_argument("--target-name", choices=["disease_cases", "hospital_admissions"], default="disease_cases")
    parser.add_argument("--location-id")
    parser.add_argument("--disease-id")
    parser.add_argument("--push-supabase", action="store_true")
    parser.add_argument("--output", default="mining_results.json")
    args = parser.parse_args()
    frame = validate_monthly_observations(pd.read_csv(Path(args.csv)))
    results = analyze_monthly(frame)
    Path(args.output).write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps([{k:v for k,v in r.items() if k != "result"} | {"result_keys": list(r["result"].keys())} for r in results], indent=2))
    if args.push_supabase:
        persist(results, args.target_name, args.location_id, args.disease_id)
        print("Persisted descriptive mining results to Supabase.")


if __name__ == "__main__":
    main()
