import pytest
from healthtrend.metrics import forecast_metrics

def test_forecast_metrics():
    result = forecast_metrics([10, 20, 30], [12, 18, 33])
    assert result['mae'] == pytest.approx(7 / 3)
    assert result['rmse'] == pytest.approx((17 / 3) ** 0.5)
    assert result['mape'] is not None

def test_zero_actuals_do_not_divide_by_zero():
    result = forecast_metrics([0, 0], [1, 2])
    assert result['mape'] is None
    assert result['mae'] == pytest.approx(1.5)

def test_mismatched_lengths_fail():
    with pytest.raises(ValueError):
        forecast_metrics([1, 2], [1])
