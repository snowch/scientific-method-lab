# Copyright © 2026 Christopher Snow
# Authored schedule and trend. See the lesson for assumptions and interpretation.
import numpy as np
import pandas as pd
rng = np.random.default_rng(42)
labels = np.array(["A", "B"] * 6)
rng.shuffle(labels)
run = pd.DataFrame({"position": np.arange(1, 13), "treatment": labels})
run["background_ms"] = 120 - 2 * run.position
print(run.to_string(index=False))
print("Mean position by treatment:")
print(run.groupby("treatment").position.mean().round(2))
