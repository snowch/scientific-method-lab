# Copyright © 2026 Christopher Snow
# Invented data. See the lesson for assumptions and interpretation.
import numpy as np
import matplotlib.pyplot as plt
a = np.array([100, 110, 90, 120, 105])
b = np.array([85, 88, 81, 96, 84])
minimum_reduction_pct = 20
reduction = 100 * (a - b) / a
print("Reduction per pair (%):", reduction.round(1))
print(f"Pairs meeting {minimum_reduction_pct:g}%:", int((reduction >= minimum_reduction_pct).sum()))
plt.bar(range(1, 6), reduction, color="#236b60")
plt.axhline(minimum_reduction_pct, color="#b36335", linestyle="--",
            label=f"Useful threshold ({minimum_reduction_pct:g}%)")
plt.xlabel("Invented comparison pair"); plt.ylabel("Elapsed-time reduction (%)")
plt.legend(); plt.tight_layout()
