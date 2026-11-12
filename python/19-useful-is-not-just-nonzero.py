# Copyright © 2026 Christopher Snow
# Invented data. See the lesson for assumptions and interpretation.
import numpy as np
from scipy import stats
a = np.array([120, 108, 132, 114, 126], dtype=float)
b = np.array([100, 100, 100, 100, 100], dtype=float)
log_ratio = np.log(a / b)
interval = stats.t.interval(.95, len(a)-1, loc=log_ratio.mean(), scale=stats.sem(log_ratio))
ratio = np.exp(log_ratio.mean())
low, high = np.exp(interval)
print("Geometric mean A/B ratio:", round(ratio, 3))
print("95% t interval for A/B ratio:", round(low, 3), round(high, 3))
print("Implied central time reduction (%):", round(100 * (1 - 1/ratio), 2))
print("Ratio needed for a 20% reduction:", 1 / .8)
