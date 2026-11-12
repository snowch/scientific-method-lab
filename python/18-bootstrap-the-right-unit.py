# Copyright © 2026 Christopher Snow
# Invented data. See the lesson for assumptions and interpretation.
import numpy as np
from scipy import stats
difference_ms = np.array([-8, -11, -5, -13, -9, -3, -12, -7])
result = stats.bootstrap((difference_ms,), np.mean,
    n_resamples=4000, method="basic", random_state=42)
print("Mean B-minus-A (ms):", difference_ms.mean())
print("95% basic bootstrap interval (ms):",
      round(result.confidence_interval.low, 3), round(result.confidence_interval.high, 3))
print("Bootstrap SE (ms):", round(result.standard_error, 3))
