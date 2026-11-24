import pytest
from healthtrend.ingestion import extract_tpc_from_mmis_text


def test_extracts_monthly_tpc_from_report_table():
    text = """GRAPH 1: BSE
GRAPH 2: MONTH WISE TREND OF TPC IN COUNTRY
Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec
TPC Current Year 9722 7725 9168 12059 15695 23175 39102 35643 33442 25486 28015 18151
TPC 3 Year Average 6690 5612 5886 7139 9418 14658 27241 27444 27360 21085 18683 15172
There is an increase of TPC by 38.09%
GRAPH 3: PF
"""
    result = extract_tpc_from_mmis_text(text, 2024, 12)
    assert len(result) == 12
    assert result.iloc[0]["cases"] == 9722
    assert result.iloc[-1]["cases"] == 18151


def test_rejects_short_report_row():
    text = "GRAPH 2 TPC Current Year 10695 7875 10827 13624 TPC 3 Year Average 1 2 3 4 GRAPH 3"
    with pytest.raises(ValueError, match="expected at least 12"):
        extract_tpc_from_mmis_text(text, 2025, 12)
