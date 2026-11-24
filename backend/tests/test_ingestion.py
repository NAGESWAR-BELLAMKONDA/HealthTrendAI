import pandas as pd
import pytest
from healthtrend.ingestion import validate_monthly_observations

def test_monthly_normalization_and_sorting():
    frame=pd.DataFrame({'date':['2024-02-15','2024-01-20'],'cases':[20,10]})
    out=validate_monthly_observations(frame)
    assert out['date'].tolist()==[pd.Timestamp('2024-01-01'),pd.Timestamp('2024-02-01')]

def test_duplicate_months_rejected():
    frame=pd.DataFrame({'date':['2024-01-01','2024-01-31'],'cases':[10,11]})
    with pytest.raises(ValueError,match='Duplicate'):
        validate_monthly_observations(frame)

def test_negative_counts_rejected():
    frame=pd.DataFrame({'date':['2024-01-01'],'cases':[-1]})
    with pytest.raises(ValueError,match='Negative'):
        validate_monthly_observations(frame)
