# Copyright © 2026 Christopher Snow
# Seeded simulation. See the lesson for assumptions and interpretation.
import numpy as np
rng = np.random.default_rng(22)
for n in [10, 100, 1000]:
    x = rng.normal(100, 15, n)
    sd = x.std(ddof=1)
    print(f"n={n:4d} mean={x.mean():.2f} SD={sd:.2f} SE={sd / np.sqrt(n):.2f} ms")
