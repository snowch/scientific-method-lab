# Copyright © 2026 Christopher Snow
# Invented data. See the lesson for assumptions and interpretation.
import numpy as np
import matplotlib.pyplot as plt
repeat_fraction = np.array([0, .25, .5, .75, 1])
prediction = 40 * repeat_fraction
observed = np.array([12, 21, 32, 41, 52])
residual = observed - prediction
print("Observed minus predicted (ms):", residual)
plt.axhline(0, color="#68736e", linestyle="--")
plt.plot(repeat_fraction, residual, "o-", color="#b36335")
plt.xlabel("Repeat fraction"); plt.ylabel("Residual saving (ms)")
plt.tight_layout()
