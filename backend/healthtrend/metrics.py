from __future__ import annotations
import numpy as np

def forecast_metrics(actual, predicted) -> dict[str, float | None]:
    y = np.asarray(actual, dtype=float).reshape(-1)
    p = np.asarray(predicted, dtype=float).reshape(-1)
    if y.size == 0 or y.size != p.size:
        raise ValueError('actual and predicted must be non-empty arrays of equal length')
    if not np.isfinite(y).all() or not np.isfinite(p).all():
        raise ValueError('metrics require finite values')
    error = y - p
    nonzero = y != 0
    mape = float(np.mean(np.abs(error[nonzero] / y[nonzero])) * 100) if nonzero.any() else None
    return {'mae': float(np.mean(np.abs(error))), 'rmse': float(np.sqrt(np.mean(error ** 2))), 'mape': mape}
