from __future__ import annotations

import argparse
import os
from pathlib import Path

import pandas as pd

from healthtrend.ingestion import load_hmis_ipd_monthly_csv, validate_monthly_observations


def upsert_ipd_to_supabase(frame: pd.DataFrame, source_names: list[str], source_urls: list[str]) -> None:
    from supabase import create_client

    client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
    source_ids = {}
    for source_name, source_url in zip(source_names, source_urls):
        source = client.table("dataset_sources").upsert({
            "source_name": source_name,
            "publisher": "Health Management Information System, Ministry of Health & Family Welfare, Government of India",
            "source_url": source_url,
            "dataset_description": "Monthly inpatient admissions from the exact HMIS M14 patient-services indicator",
            "geography": ", ".join(sorted(frame["state"].dropna().astype(str).unique())),
            "refresh_frequency": "Monthly",
            "last_checked_at": pd.Timestamp.now(tz="UTC").isoformat(),
        }, on_conflict="source_url").execute().data[0]
        source_ids[source_url] = source["id"]

    location_ids = {}
    for row in frame.to_dict(orient="records"):
        state = str(row["state"])
        district = str(row["district"]) if pd.notna(row.get("district")) else None
        if state.casefold() == "all india":
            location = {
                "country_code": "IN", "country_name": "India",
                "admin1_name": None, "admin2_name": None,
                "location_label": "India — National",
            }
        else:
            location = {
                "country_code": "IN", "country_name": "India",
                "admin1_name": state, "admin2_name": district,
                "location_label": district or state,
            }
        key = (state, district)
        if key not in location_ids:
            saved = client.table("dim_location").upsert(
                location,
                on_conflict="country_name,admin1_name,admin2_name,location_label",
            ).execute().data[0]
            location_ids[key] = saved["id"]

    date_rows = []
    for dt in pd.to_datetime(frame["date"]).drop_duplicates():
        date_rows.append({
            "date_key": int(dt.strftime("%Y%m%d")), "full_date": dt.strftime("%Y-%m-%d"),
            "year": dt.year, "quarter": (dt.month - 1) // 3 + 1, "month": dt.month,
            "month_name": dt.strftime("%B"), "week_of_year": int(dt.strftime("%V")),
            "day_of_month": dt.day, "day_of_week": dt.isoweekday(),
            "is_weekend": dt.isoweekday() >= 6,
        })
    client.table("dim_date").upsert(date_rows, on_conflict="date_key").execute()

    facts = []
    for row in frame.to_dict(orient="records"):
        dt = pd.Timestamp(row["date"])
        state = str(row["state"])
        district = str(row["district"]) if pd.notna(row.get("district")) else None
        facts.append({
            "date_key": int(dt.strftime("%Y%m%d")),
            "location_id": location_ids[(state, district)],
            "source_id": source_ids[row["source_url"]],
            "admission_count": float(row["cases"]),
            "measure_unit": "inpatient admissions",
            "is_estimated": False,
            "source_note": row.get("source_note") or None,
            "source_record_id": f"HMIS-IPD-{state}-{district or 'NATIONAL'}-{dt:%Y-%m}",
        })
    client.table("fact_hospital_admissions").upsert(
        facts, on_conflict="date_key,location_id,disease_id,source_id,source_record_id"
    ).execute()
    for source_id in source_ids.values():
        client.table("dataset_sources").update({
            "is_active": True,
            "last_loaded_at": pd.Timestamp.now(tz="UTC").isoformat(),
        }).eq("id", source_id).execute()


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest monthly HMIS inpatient admissions.")
    parser.add_argument("--input", action="append", required=True, help="Downloaded HMIS CSV; repeat once per fiscal year.")
    parser.add_argument("--state", default="All India")
    parser.add_argument("--district", default=None)
    parser.add_argument("--source-name", action="append", required=True, help="Source title; repeat in the same order as --input.")
    parser.add_argument("--source-url", action="append", required=True, help="Source dataset URL; repeat in the same order as --input.")
    parser.add_argument("--output", default="../../data/processed/hmis_ipd_monthly.csv")
    parser.add_argument("--push-supabase", action="store_true")
    args = parser.parse_args()

    if not (len(args.input) == len(args.source_name) == len(args.source_url)):
        parser.error("Repeat --input, --source-name and --source-url the same number of times and in matching order.")

    frames = []
    for input_path, source_url in zip(args.input, args.source_url):
        part = load_hmis_ipd_monthly_csv(input_path, state=args.state, district=args.district)
        part["source_url"] = source_url
        frames.append(part)
    frame = validate_monthly_observations(pd.concat(frames, ignore_index=True), date_col="date", value_col="cases")
    if frame.empty:
        raise ValueError("No validated HMIS monthly inpatient observations were produced")

    output = (Path(__file__).resolve().parent / args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output, index=False)
    print(f"Validated {len(frame)} monthly inpatient observations: {frame['date'].min()} to {frame['date'].max()}")
    print(f"Saved {output}")
    if args.push_supabase:
        upsert_ipd_to_supabase(frame, args.source_name, args.source_url)
        print("Upserted HMIS sources, dimensions and inpatient facts to Supabase")


if __name__ == "__main__":
    main()
