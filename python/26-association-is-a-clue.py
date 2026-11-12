# Copyright © 2026 Christopher Snow
# Seeded causal model. See the lesson for assumptions and interpretation.
import numpy as np
import matplotlib.pyplot as plt
rng = np.random.default_rng(111)
load = rng.uniform(0, 1, 120)
queue = 20 * load + rng.normal(0, 1, len(load))
response = 50 + 100 * load + rng.normal(0, 5, len(load))
print("Observed correlation:", round(np.corrcoef(queue, response)[0, 1], 3))
plt.scatter(queue, response, c=load, cmap="viridis", s=25)
plt.colorbar(label="Common input: background load")
plt.xlabel("Queue-length model output"); plt.ylabel("Response-time model output (ms)")
plt.tight_layout()
