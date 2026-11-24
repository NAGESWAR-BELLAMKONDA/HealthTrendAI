from __future__ import annotations

import argparse
import os
from pathlib import Path

import pandas as pd

from healthtrend.ingestion import validate_monthly_observations
from healthtrend.mining import mine_monthly_series


def persist(outputs: list[dict], target_name: str) -> None:
    from supabase import create_client

    client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
    for item in outputs:
        payload = {
            **item,
            "target_name": target_name,
            "location_id": None,
            "disease_id": None,
        }
        client.table("mining_results").insert(payload).execute()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run reproducible monthly disease/admissions mining.")
    parser.add_argument("--csv", required=True)
    parser.add_argument("--target-name", choices=["disease_cases", "hospital_admissions"], default="disease_cases")
    parser.add_argument("--push-supabase", action="store_true")
    args = parser.parse_args()
    frame = validate_monthly_observations(pd.read_csv(Path(args.csv)), "date", "cases")
    outputs = mine_monthly_series(frame)
    for item in outputs:
        print(f"{item['analysis_type']}: {item['status']} (n={item['sample_size']})")
    if args.push_supabase:
        persist(outputs, args.target_name)
        print(f"Persisted {len(outputs)} mining analyses to Supabase.")


if __name__ == "__main__":
    main()
