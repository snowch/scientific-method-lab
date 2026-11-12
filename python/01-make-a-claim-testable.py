# Copyright © 2026 Christopher Snow
# Invented data. See the lesson for assumptions and interpretation.
import numpy as np
import matplotlib.pyplot as plt
a = np.array([100, 110, 90, 120, 105])
b = np.array([85, 88, 81, 96, 84])
reduction = 100 * (a - b) / a
print("Reduction per pair (%):", reduction.round(1))
print("Pairs meeting 20%:", int((reduction >= 20).sum()))
plt.bar(range(1, 6), reduction, color="#236b60")
plt.axhline(20, color="#b36335", linestyle="--", label="Useful threshold")
plt.xlabel("Invented comparison pair"); plt.ylabel("Elapsed-time reduction (%)")
plt.legend(); plt.tight_layout()
