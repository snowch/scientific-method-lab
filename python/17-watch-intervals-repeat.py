# Copyright © 2026 Christopher Snow
# Seeded simulation. See the lesson for assumptions and interpretation.
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
rng = np.random.default_rng(51)
x = rng.normal(100, 15, (500, 12))
means = x.mean(axis=1)
margin = stats.t.ppf(.975, 11) * x.std(axis=1, ddof=1) / np.sqrt(12)
low, high = means - margin, means + margin
covered = (low <= 100) & (high >= 100)
print("Intervals:", len(x), "Covering true mean:", int(covered.sum()))
print("Coverage fraction:", round(covered.mean(), 3))
for i in range(30):
    plt.plot([low[i], high[i]], [i, i], color="#236b60" if covered[i] else "#b36335")
    if not covered[i]: plt.scatter(means[i], i, marker="x", color="#b36335")
plt.axvline(100, color="#68736e", linestyle="--", label="True mean")
plt.xlabel("95% interval for mean elapsed time (ms)"); plt.ylabel("Simulated experiment")
plt.legend(); plt.tight_layout()
