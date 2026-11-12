# Copyright © 2026 Christopher Snow
# Seeded simulation. See the lesson for assumptions and interpretation.
import numpy as np
from scipy import stats
rng = np.random.default_rng(91)
m = 20
x = rng.normal(size=(600, m, 25))
p = stats.ttest_1samp(x, 0, axis=2).pvalue
print("Any p<0.05 fraction:", round((p < .05).any(axis=1).mean(), 3))
print("Independent-test formula:", round(1 - .95**m, 3))
print("Any Bonferroni rejection fraction:", round((p < .05/m).any(axis=1).mean(), 3))
