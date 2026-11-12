# Copyright © 2026 Christopher Snow
# Seeded null simulation. See the lesson for assumptions and interpretation.
import numpy as np
import matplotlib.pyplot as plt
rng = np.random.default_rng(17)
null_means = rng.normal(0, 10, (5000, 20)).mean(axis=1)
observed_mean = -5.0
extreme = np.abs(null_means) >= abs(observed_mean)
print("Simulated null experiments:", len(null_means))
print("Fraction at least as extreme:", round(extreme.mean(), 4))
plt.hist(null_means, bins=35, color="#236b60", alpha=.8)
plt.axvline(observed_mean, color="#b36335", label="Observed statistic")
plt.xlabel("Mean difference under null model (ms)"); plt.ylabel("Simulated experiments")
plt.legend(); plt.tight_layout()
