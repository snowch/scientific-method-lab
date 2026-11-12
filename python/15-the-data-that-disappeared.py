# Copyright © 2026 Christopher Snow
# Invented data. See the lesson for assumptions and interpretation.
import pandas as pd
data = pd.DataFrame({"request": range(1, 7),
    "status": ["ok", "ok", "timeout", "ok", "timeout", "ok"],
    "elapsed_ms": [80, 90, None, 85, None, 95]})
print(data.to_string(index=False))
print("Offered requests:", len(data))
print("Outcome counts:", data.status.value_counts().to_dict())
print("Mean among recorded times (ms):", data.elapsed_ms.mean())
