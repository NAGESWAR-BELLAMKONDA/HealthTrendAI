import pandas as pd
import pytest
from healthtrend.models import compare_six_models

def test_model_comparison_requires_enough_months():
    frame=pd.DataFrame({'date':pd.date_range('2024-01-01',periods=16,freq='MS'),'cases':range(16)})
    with pytest.raises(ValueError,match='at least 36'):
        compare_six_models(frame)

def test_model_comparison_rejects_month_gaps():
    dates=list(pd.date_range('2020-01-01',periods=37,freq='MS'))
    dates.pop(10)
    frame=pd.DataFrame({'date':dates,'cases':range(36)})
    with pytest.raises(ValueError,match='gaps'):
        compare_six_models(frame)
