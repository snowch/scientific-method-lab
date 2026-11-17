# Copyright © 2026 Christopher Snow
# Invented data. See the lesson for assumptions and interpretation.
import numpy as np
import matplotlib.pyplot as plt
elapsed = np.array([150, 140, 132, 125, 119, 114, 110, 107, 104, 102, 101, 100])
labels = np.repeat(["A", "B"], 6)
print("Run labels:", labels)
print("Mean time for A (ms):", elapsed[labels == "A"].mean())
print("Mean time for B (ms):", elapsed[labels == "B"].mean())
plt.plot(np.arange(1, 13), elapsed, "-", color="#68736e")
positions = np.arange(1, len(elapsed) + 1)
plt.scatter(positions[labels == "A"], elapsed[labels == "A"], marker="o", color="#236b60", label="A")
plt.scatter(positions[labels == "B"], elapsed[labels == "B"], marker="s", color="#b36335", label="B")
plt.legend()
plt.xlabel("Observation order"); plt.ylabel("Elapsed time (ms)")
plt.tight_layout()
