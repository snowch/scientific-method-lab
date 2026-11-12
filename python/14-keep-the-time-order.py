# Copyright © 2026 Christopher Snow
# Invented data. See the lesson for assumptions and interpretation.
import numpy as np
import matplotlib.pyplot as plt
elapsed = np.array([150, 140, 132, 125, 119, 114, 110, 107, 104, 102, 101, 100])
print("First-half mean (ms):", elapsed[:6].mean())
print("Second-half mean (ms):", elapsed[6:].mean())
plt.plot(np.arange(1, 13), elapsed, "o-", color="#236b60")
plt.axvline(6.5, linestyle="--", color="#b36335")
plt.xlabel("Observation order"); plt.ylabel("Elapsed time (ms)")
plt.tight_layout()
