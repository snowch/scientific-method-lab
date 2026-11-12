# Copyright © 2026 Christopher Snow
# Invented data. See the lesson for assumptions and interpretation.
import pandas as pd
import matplotlib.pyplot as plt
table = pd.DataFrame({"workload": ["unique", "repeated"],
    "off_ms": [100, 100], "on_ms": [110, 60]})
table["cache_effect_ms"] = table.on_ms - table.off_ms
print(table.to_string(index=False))
print("Difference of effects (ms):", table.cache_effect_ms.iloc[1] - table.cache_effect_ms.iloc[0])
for row in table.itertuples():
    plt.plot([0, 1], [row.off_ms, row.on_ms], "o-", label=row.workload)
plt.xticks([0, 1], ["Cache off", "Cache on"]); plt.ylabel("Elapsed time (ms)")
plt.legend(title="Workload"); plt.tight_layout()
