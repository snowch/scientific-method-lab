# Copyright © 2026 Christopher Snow
# Seeded simulation. See the lesson for assumptions and interpretation.
import numpy as np
from scipy import stats
rng = np.random.default_rng(73)
effect_ms, sd_ms = 3, 10
for n in [10, 30, 100]:
    experiments = rng.normal(effect_ms, sd_ms, (600, n))
    p = stats.ttest_1samp(experiments, popmean=0, axis=1).pvalue
    print(f"n={n:3d} simulated detection fraction={(p < .05).mean():.3f}")
