from __future__ import annotations

import calendar
import re
from pathlib import Path
from typing import Iterable

import pandas as pd

MONTHS = {name.lower(): i for i, name in enumerate(calendar.month_name) if name}
MONTHS.update({name.lower(): i for i, name in enumerate(calendar.month_abbr) if name})


def validate_monthly_observations(frame: pd.DataFrame, date_col: str = "date", value_col: str = "cases") -> pd.DataFrame:
    required = {date_col, value_col}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    out = frame.copy()
    out[date_col] = pd.to_datetime(out[date_col], errors="coerce").dt.to_period("M").dt.to_timestamp()
    out[value_col] = pd.to_numeric(out[value_col], errors="coerce")
    out = out.dropna(subset=[date_col, value_col]).sort_values(date_col)
    if (out[value_col] < 0).any():
        raise ValueError("Negative counts are not valid observations")
    if out[date_col].duplicated().any():
        raise ValueError("Duplicate month observations found; resolve source duplicates explicitly")
    return out.reset_index(drop=True)


def extract_tpc_from_mmis_pdf(pdf_path: str | Path, year: int, report_month: int) -> pd.DataFrame:
    """Extract the national TPC Current Year row from an NCVBDC MMIS PDF.

    Only months up to report_month are emitted. This parser deliberately fails
    closed if the report table cannot be interpreted; it never fills missing months.
    """
    try:
        import pdfplumber
    except ImportError as exc:
        raise RuntimeError("Install pdfplumber to parse NCVBDC MMIS PDFs") from exc

    if not 1 <= report_month <= 12:
        raise ValueError("report_month must be 1..12")

    with pdfplumber.open(str(pdf_path)) as pdf:
        text = "\\n".join(page.extract_text() or "" for page in pdf.pages)

    start = text.upper().find("GRAPH 2")
    end = text.upper().find("GRAPH 3", start + 1)
    if start < 0 or end < 0:
        raise ValueError("Could not locate the TPC table in the MMIS report")
    section = text[start:end]
    row_match = re.search(
        r"TPC\\s+Current\\s+Year(.*?)(?:TPC\\s+3\\s+Year\\s+Average|There is an increase)",
        section,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not row_match:
        raise ValueError("Could not locate the TPC Current Year row")

    raw_values = re.findall(r"(?<![A-Za-z])\\d[\\d,]*", row_match.group(1))
    values = [int(v.replace(",", "")) for v in raw_values]
    if len(values) < report_month:
        raise ValueError(f"Report contains {len(values)} TPC values, expected at least {report_month}")
    rows = [
        {"date": pd.Timestamp(year=year, month=m, day=1), "cases": values[m - 1],
         "country": "India", "disease": "Malaria", "indicator": "TPC"}
        for m in range(1, report_month + 1)
    ]
    return validate_monthly_observations(pd.DataFrame(rows))


def load_mmis_pdf_files(reports: Iterable[tuple[str, int, int]]) -> pd.DataFrame:
    """Load tuples of (pdf_path, report_year, last_reported_month)."""
    frames = [extract_tpc_from_mmis_pdf(path, year, month) for path, year, month in reports]
    if not frames:
        raise ValueError("No MMIS report files supplied")
    combined = pd.concat(frames, ignore_index=True)
    return validate_monthly_observations(combined)


def load_hmis_monthly_csv(path: str | Path, indicator_pattern: str) -> pd.DataFrame:
    """Normalize an HMIS monthly CSV after the source-specific file is obtained.

    This does not assume all HMIS indicators are disease cases. The caller must
    explicitly select a documented indicator (e.g. IPD attendance) and keep its
    measurement name separate from disease-case counts.
    """
    raw = pd.read_csv(path)
    required = {"fiscal_year", "month", "state", "indicator", "value"}
    if not required.issubset(raw.columns):
        raise ValueError(f"HMIS CSV must contain columns: {sorted(required)}")
    selected = raw[raw["indicator"].astype(str).str.contains(indicator_pattern, case=False, regex=True, na=False)].copy()
    if selected.empty:
        raise ValueError("No HMIS rows matched the explicitly configured indicator")
    def month_start(row: pd.Series) -> pd.Timestamp:
        month = MONTHS.get(str(row["month"]).strip().lower())
        if not month:
            raise ValueError(f"Unknown HMIS month: {row['month']}")
        fy = str(row["fiscal_year"])
        start_year = int(fy[:4])
        # HMIS fiscal year is April-March; month determines calendar year.
        year = start_year if month >= 4 else start_year + 1
        return pd.Timestamp(year=year, month=month, day=1)
    selected["date"] = selected.apply(month_start, axis=1)
    selected["value"] = pd.to_numeric(selected["value"], errors="coerce")
    selected = selected.dropna(subset=["value"])
    if (selected["value"] < 0).any():
        raise ValueError("HMIS contains negative counts; inspect source records")
    return selected
