# Copyright © 2026 Christopher Snow
# Authored instrument model. See the lesson for assumptions and interpretation.
import numpy as np
reference_ms = np.array([11, 12, 13, 14, 21, 22])
resolution_ms = 10
displayed = np.round(reference_ms / resolution_ms) * resolution_ms
print("Reference (ms):", reference_ms)
print("Displayed (ms):", displayed)
print("With a +5 ms offset:", reference_ms + 5)
