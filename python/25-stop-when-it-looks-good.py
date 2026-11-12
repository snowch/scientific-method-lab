# Copyright © 2026 Christopher Snow
# Seeded simulation. See the lesson for assumptions and interpretation.
import numpy as np
from scipy import stats
rng = np.random.default_rng(101)
x = rng.normal(size=(600, 100))
looks = [20, 40, 60, 80, 100]
p = np.column_stack([stats.ttest_1samp(x[:, :n], 0, axis=1).pvalue for n in looks])
print("Fixed final-test rejection fraction:", round((p[:, -1] < .05).mean(), 3))
print("Any interim crossing fraction:", round((p < .05).any(axis=1).mean(), 3))
print("Planned observation counts:", looks)
