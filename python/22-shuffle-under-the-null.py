# Copyright © 2026 Christopher Snow
# Invented data. See the lesson for assumptions and interpretation.
import numpy as np
from scipy import stats
a = np.array([80, 130, 200, 105, 160, 95, 140, 175])
b = np.array([72, 119, 187, 98, 150, 91, 129, 168])
def difference(a, b):
    return np.mean(b - a)
test = stats.permutation_test((a, b), difference,
    permutation_type="samples", n_resamples=np.inf, alternative="two-sided")
print("Mean B-minus-A (ms):", test.statistic)
print("Exact assignment patterns:", len(test.null_distribution))
print("Two-sided permutation p-value:", test.pvalue)
