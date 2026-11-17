# Copyright © 2026 Christopher Snow
# Invented data. See the lesson for assumptions and interpretation.
import numpy as np
from scipy import stats
x = np.array([101, 97, 104, 100, 98, 103, 99, 102])
se = stats.sem(x)
confidence_level = 0.95
low, high = stats.t.interval(confidence_level, df=len(x)-1, loc=x.mean(), scale=se)
print("Sample mean (ms):", round(x.mean(), 3))
print("Estimated SE (ms):", round(se, 3))
print(f"{confidence_level:.0%} t interval for population mean (ms):", round(low, 3), round(high, 3))
print("Observed range (ms):", x.min(), x.max())
