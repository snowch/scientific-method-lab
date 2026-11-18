# Copyright © 2026 Christopher Snow
# Measured at execution. See the lesson for assumptions and interpretation.
import time
import numpy as np
import pandas as pd
block_count = 12
include_set_construction = False
rng = np.random.default_rng(121)
values = list(range(2000))
queries = rng.integers(0, 3000, 400).tolist()
containers = {"A": values, "B": set(values)}
def lookup(container):
    return sum(q in container for q in queries)
expected = lookup(containers["A"])
assert lookup(containers["B"]) == expected
rows = []
for block in range(1, block_count + 1):
    order = rng.permutation(["A", "B"]).tolist()
    row = {"run_id": f"block-{block}", "order": "".join(order)}
    for name in order:
        if include_set_construction and name == "B":
            start = time.perf_counter_ns()
            answer = lookup(set(values))
        else:
            start = time.perf_counter_ns()
            answer = lookup(containers[name])
        elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000
        assert answer == expected
        row[name.lower() + "_ms"] = elapsed_ms
    rows.append(row)
data = pd.DataFrame(rows)[["run_id", "order", "a_ms", "b_ms"]]
boundary = "B includes set construction" if include_set_construction else "construction excluded"
print(f"MEASURED: local Python lookups ({boundary}).")
print("Paired blocks share one runtime; independence is not established.")
print(data.to_csv(index=False, float_format="%.6f"))
