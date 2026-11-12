# Copyright © 2026 Christopher Snow
# Seeded simulation. See the lesson for assumptions and interpretation.
import numpy as np
from scipy import stats
rng = np.random.default_rng(81)
effect_ms = .2
for n in [30, 3000, 30000]:
    x = rng.normal(effect_ms, 1, n)
    test = stats.ttest_1samp(x, 0)
    print(f"n={n:5d} mean={x.mean():.3f} ms p={test.pvalue:.5g}")
