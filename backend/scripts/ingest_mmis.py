from __future__ import annotations

import argparse
import os
from pathlib import Path

import pandas as pd
import requests

from healthtrend.ingestion import extract_tpc_from_mmis_pdf, validate_monthly_observations

REPORTS = [
    {
        "year": 2024, "last_month": 12, "report_period": "December 2024",
        "url": "https://www.ncvbdc.mohfw.gov.in/Doc/MMIS/2024/MMIS-Report-Country-Dec-2024.pdf",
    },
    {
        "year": 2025, "last_month": 4, "report_period": "April 2025",
        "url": "https://ncvbdc.mohfw.gov.in/Doc/MMIS/2025/MMIS%20Report-Country_April-2025.pdf",
    },
]


def download_reports(raw_dir: Path) -> pd.DataFrame:
    raw_dir.mkdir(parents=True, exist_ok=True)
    frames = []
    for report in REPORTS:
        filename = f"mmis_country_{report['year']}_{report['last_month']:02d}.pdf"
        path = raw_dir / filename
        response = requests.get(report["url"], timeout=60)
        response.raise_for_status()
        if "pdf" not in response.headers.get("content-type", "").lower() and not response.content.startswith(b"%PDF"):
            raise RuntimeError(f"Source did not return a PDF: {report['url']}")
        path.write_bytes(response.content)
        frame = extract_tpc_from_mmis_pdf(path, report["year"], report["last_month"])
        frame["source_report_period"] = report["report_period"]
        frame["source_pdf_url"] = report["url"]
        frames.append(frame)
    combined = validate_monthly_observations(pd.concat(frames, ignore_index=True))
    if len(combined) != sum(x["last_month"] for x in REPORTS):
        raise ValueError("Unexpected number of observations; check report overlap or parsing")
    return combined


def upsert_supabase(frame: pd.DataFrame) -> None:
    from supabase import create_client
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    client = create_client(url, key)

    source_ids = {}
    for report in REPORTS:
        record = {
            "source_name": f"MMIS National Malaria TPC — {report['report_period']}",
            "publisher": "NCVBDC, Directorate General of Health Services, MoHFW, Government of India",
            "source_url": report["url"],
            "dataset_description": f"National month-wise malaria Total Positive Cases (TPC) through {report['report_period']}",
            "geography": "India (national)",
            "refresh_frequency": "Monthly report publication",
            "last_checked_at": pd.Timestamp.now(tz="UTC").isoformat(),
            "last_loaded_at": pd.Timestamp.now(tz="UTC").isoformat(),
        }
        saved = client.table("dataset_sources").upsert(record, on_conflict="source_url").execute()
        source_ids[report["url"]] = saved.data[0]["id"]

    location = client.table("dim_location").upsert(
        {"country_code": "IN", "country_name": "India", "location_label": "India — National"},
        on_conflict="country_name,admin1_name,admin2_name,location_label",
    ).execute().data[0]
    disease = client.table("dim_disease").upsert(
        {"disease_code": "MALARIA", "disease_name": "Malaria", "disease_category": "Vector-borne disease"},
        on_conflict="disease_code,disease_name,disease_category,icd_code",
    ).execute().data[0]

    date_rows = []
    for dt in pd.to_datetime(frame["date"]):
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
        report_url = row["source_pdf_url"]
        dt = pd.Timestamp(row["date"])
        facts.append({
            "date_key": int(dt.strftime("%Y%m%d")), "location_id": location["id"],
            "disease_id": disease["id"], "source_id": source_ids[report_url],
            "case_count": float(row["cases"]), "measure_unit": "positive malaria cases",
            "is_estimated": False, "source_record_id": f"TPC-{dt:%Y-%m}",
        })
    client.table("fact_disease_cases").upsert(
        facts, on_conflict="date_key,location_id,disease_id,source_id,source_record_id"
    ).execute()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="../data/processed/india_malaria_monthly_tpc.csv")
    parser.add_argument("--push-supabase", action="store_true")
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    frame = download_reports(repo_root / "data" / "raw")
    output = (Path(__file__).resolve().parent / args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output, index=False)
    print(f"Validated {len(frame)} monthly observations: {frame['date'].min()} to {frame['date'].max()}")
    print(f"Saved {output}")
    if args.push_supabase:
        upsert_supabase(frame)
        print("Upserted dataset sources, date dimension and malaria case facts to Supabase")


if __name__ == "__main__":
    main()
