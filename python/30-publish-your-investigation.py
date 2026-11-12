# Copyright © 2026 Christopher Snow
# Invented data. See the lesson for assumptions and interpretation.
import os
import numpy as np
import pandas as pd
from scipy import stats
path = "data.csv"
if os.path.exists(path):
    data = pd.read_csv(path)
    print("INPUT: uploaded CSV; provenance and independence require your justification.")
else:
    data = pd.DataFrame({"run_id": [f"example-{i}" for i in range(1, 9)],
        "a_ms": [120, 108, 132, 114, 126, 116, 128, 118],
        "b_ms": [100, 100, 100, 100, 100, 100, 100, 100]})
    print("INPUT: INVENTED starter data, not measurements.")
required = {"run_id", "a_ms", "b_ms"}
assert required.issubset(data.columns), "Need run_id, a_ms, b_ms columns"
assert len(data) >= 5, "Use at least five paired runs for this exercise"
assert data.run_id.notna().all() and data.run_id.is_unique, "Run IDs must be present and unique"
times = data[["a_ms", "b_ms"]].to_numpy(dtype=float)
assert np.isfinite(times).all() and (times > 0).all(), "Times must be positive finite milliseconds"
logs = np.log(times[:, 0] / times[:, 1])
assert logs.std(ddof=1) > 0, "Identical ratios: t interval is degenerate; investigate the data"
interval = stats.t.interval(.95, len(logs)-1, loc=logs.mean(), scale=stats.sem(logs))
ratio = np.exp(logs.mean())
print("Pairs:", len(logs))
print("Geometric mean A/B ratio:", round(ratio, 4))
print("Approximate 95% t interval for A/B:", np.exp(interval).round(4))
print("Central B time reduction (%):", round(100 * (1 - 1/ratio), 2))
print("20% reduction requires A/B >= 1.25.")
print("Conditional inference: justify independent stable paired runs and approximately normal log ratios.")
