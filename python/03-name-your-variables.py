# Copyright © 2026 Christopher Snow
# Invented data. See the lesson for assumptions and interpretation.
import pandas as pd
data = pd.DataFrame({
    "cache": ["off", "off", "on", "on"],
    "requests": [1000, 1000, 500, 500],
    "elapsed_ms": [100, 104, 52, 50]})
data["ms_per_request"] = data.elapsed_ms / data.requests
print(data.to_string(index=False))
