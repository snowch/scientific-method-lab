# Copyright © 2026 Christopher Snow
# Invented data. See the lesson for assumptions and interpretation.
import pandas as pd
import matplotlib.pyplot as plt
pairs = pd.DataFrame({"machine": ["M1", "M2", "M3", "M4", "M5"],
    "a_ms": [80, 130, 200, 105, 160], "b_ms": [72, 119, 187, 98, 150]})
pairs["b_minus_a"] = pairs.b_ms - pairs.a_ms
print(pairs.to_string(index=False))
for row in pairs.itertuples():
    plt.plot([0, 1], [row.a_ms, row.b_ms], "o-", label=row.machine)
plt.xticks([0, 1], ["A", "B"]); plt.ylabel("Elapsed time (ms)")
plt.legend(title="Matched machine"); plt.tight_layout()
