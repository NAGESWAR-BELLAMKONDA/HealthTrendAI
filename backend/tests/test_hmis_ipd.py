import pandas as pd
import pytest
from healthtrend.ingestion import load_hmis_ipd_monthly_csv


def test_load_hmis_state_month_ipd_csv(tmp_path):
    frame = pd.DataFrame({
        "fiscal_year": ["2020-21", "2020-21"],
        "month": ["April", "May"],
        "state": ["All India", "All India"],
        "indicator": [
            "Total number of patients admitted (Inpatients) during the month (sum of items 14.10.1.a and 14.10.1.b)",
            "Total number of patients admitted (Inpatients) during the month (sum of items 14.10.1.a and 14.10.1.b)",
        ],
        "category": ["TOTAL", "TOTAL"],
        "value": [1000, 1100],
    })
    path = tmp_path / "hmis.csv"
    frame.to_csv(path, index=False)
    out = load_hmis_ipd_monthly_csv(path)
    assert out["date"].tolist() == [pd.Timestamp("2020-04-01"), pd.Timestamp("2020-05-01")]
    assert out["cases"].tolist() == [1000, 1100]


def test_load_hmis_subdistrict_ipd_sums_only_combined_facility_total(tmp_path):
    frame = pd.DataFrame({
        "fiscal_year": ["2014-15", "2014-15", "2014-15"],
        "month": ["January", "January", "January"],
        "state": ["Gujarat", "Gujarat", "Gujarat"],
        "district_as_per_lgd": ["Dangs", "Dangs", "Dangs"],
        "sub_district": ["Vaghai", "Ahwa", "Vaghai"],
        "indicator": ["Total number of patients admitted (Inpatients) during the month"] * 3,
        "facility_category": [
            "Public and Private Facilities OR Rural and Urban Facilities",
            "Public and Private Facilities OR Rural and Urban Facilities",
            "Public",
        ],
        "category": ["Total", "Total", "Total"],
        "value": [93, 57, 30],
    })
    path = tmp_path / "hmis_district.csv"
    frame.to_csv(path, index=False)
    out = load_hmis_ipd_monthly_csv(path, state="Gujarat", district="Dangs")
    assert len(out) == 1
    assert out.iloc[0]["cases"] == 150


def test_load_hmis_ipd_requires_exact_indicator(tmp_path):
    frame = pd.DataFrame({
        "fiscal_year": ["2020-21"], "month": ["April"], "state": ["All India"],
        "indicator": ["Total OPD patients"], "category": ["TOTAL"], "value": [500],
    })
    path = tmp_path / "wrong_indicator.csv"
    frame.to_csv(path, index=False)
    with pytest.raises(ValueError, match="indicator"):
        load_hmis_ipd_monthly_csv(path)
