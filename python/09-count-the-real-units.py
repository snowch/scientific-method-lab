# Copyright © 2026 Christopher Snow
# Seeded simulation. See the lesson for assumptions and interpretation.
import numpy as np
rng = np.random.default_rng(31)
readings = 100 + rng.normal(0, 12, (6, 1)) + rng.normal(0, 1, (6, 20))
session_means = readings.mean(axis=1)
naive_se = readings.std(ddof=1) / np.sqrt(readings.size)
block_se = session_means.std(ddof=1) / np.sqrt(len(session_means))
print("Sessions, readings/session:", readings.shape)
print("SE assuming independent readings (ms):", round(naive_se, 2))
print("SE across session means (ms):", round(block_se, 2))
print("Session means (ms):", session_means.round(2))
