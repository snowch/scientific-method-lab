# Copyright © 2026 Christopher Snow
# Invented data. See the lesson for assumptions and interpretation.
import numpy as np
import matplotlib.pyplot as plt
a = np.array([48, 49, 50, 51, 52])
b = np.array([10, 10, 10, 10, 210])
print("Means (ms):", a.mean(), b.mean())
print("Medians (ms):", np.median(a), np.median(b))
plt.scatter(a, np.linspace(-.08, .08, len(a)), label="A", color="#236b60")
plt.scatter(b, 1 + np.linspace(-.08, .08, len(b)), label="B", marker="s", color="#b36335")
plt.axvline(a.mean(), linestyle="--", color="#68736e")
plt.yticks([0, 1], ["Service A", "Service B"]); plt.xlabel("Response time (ms)")
plt.tight_layout()
