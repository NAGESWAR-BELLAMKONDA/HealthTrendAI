from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import pandas as pd
from healthtrend.models import compare_six_models


def persist_results(results, frame: pd.DataFrame, target_name: str, location_id: str | None = None, disease_id: str | None = None) -> None:
    from supabase import create_client

    client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
    dates = pd.to_datetime(frame["date"])
    split = max(24, int(len(frame) * 0.8))
    if split >= len(frame) - 1:
        split = len(frame) - 1
    training_start = dates.iloc[0].date().isoformat()
    training_end = dates.iloc[split - 1].date().isoformat()
    test_start = dates.iloc[split].date().isoformat()
    test_end = dates.iloc[-1].date().isoformat()

    for result in results:
        family = "machine_learning" if result.model_name in {"Decision Tree", "Random Forest", "XGBoost"} else "time_series"
        run = client.table("model_runs").insert({
            "target_name": target_name,
            "location_id": location_id,
            "disease_id": disease_id,
            "model_name": result.model_name,
            "model_family": family,
            "training_start": training_start,
            "training_end": training_end,
            "test_start": test_start,
            "test_end": test_end,
            "horizon_days": 30,
            "mae": result.metrics["mae"],
            "rmse": result.metrics["rmse"],
            "mape": result.metrics["mape"],
            "status": "completed",
            "parameters": {"evaluation": "rolling_one_step_ahead"},
            "metrics_details": {"sample_count": len(result.predictions), "target_name": target_name},
        }).execute().data[0]

        forecasts = [{
            "model_run_id": run["id"],
            "forecast_date": row["date"],
            "target_name": target_name,
            "predicted_value": row["predicted"],
            "actual_value": row["actual"],
        } for row in result.predictions]
        if forecasts:
            client.table("forecast_results").upsert(
                forecasts, on_conflict="model_run_id,forecast_date,target_name"
            ).execute()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--target-name", choices=["disease_cases", "hospital_admissions"], default="disease_cases")
    parser.add_argument("--location-id", default=None)
    parser.add_argument("--disease-id", default=None)
    parser.add_argument("--push-supabase", action="store_true")
    args = parser.parse_args()

    frame = pd.read_csv(Path(args.csv))
    results = compare_six_models(frame)
    output = [{"model": r.model_name, "metrics": r.metrics, "predictions": r.predictions} for r in results]
    print(json.dumps(output, indent=2))
    if args.push_supabase:
        persist_results(results, frame, args.target_name, args.location_id, args.disease_id)
        print("Persisted model runs and forecast observations to Supabase")


if __name__ == "__main__":
    main()
