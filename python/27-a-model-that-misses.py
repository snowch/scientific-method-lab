# Copyright © 2026 Christopher Snow
# Authored model. See the lesson for assumptions and interpretation.
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
size = np.arange(1, 11)
elapsed = 20 + 2 * size**2
fit = stats.linregress(size, elapsed)
prediction = fit.intercept + fit.slope * size
residual = elapsed - prediction
print("Slope (ms per size unit):", round(fit.slope, 3))
print("Residuals (ms):", residual.round(2))
plt.axhline(0, color="#68736e", linestyle="--")
plt.plot(size, residual, "o-", color="#b36335")
plt.xlabel("Tested input size"); plt.ylabel("Observed minus fitted time (ms)")
plt.tight_layout()
