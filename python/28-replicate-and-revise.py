# Copyright © 2026 Christopher Snow
# Invented data. See the lesson for assumptions and interpretation.
import pandas as pd
data = pd.DataFrame({"environment": ["laptop"]*4 + ["phone"]*4,
    "a_ms": [100, 105, 95, 110, 100, 105, 95, 110],
    "b_ms": [75, 79, 72, 83, 110, 116, 104, 121]})
data["reduction_pct"] = 100 * (data.a_ms - data.b_ms) / data.a_ms
print(data.to_string(index=False))
print("Mean reduction (%) by environment:")
print(data.groupby("environment").reduction_pct.mean().round(2))
print("Pooled mean reduction (%):", round(data.reduction_pct.mean(), 2))
