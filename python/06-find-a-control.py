# Copyright © 2026 Christopher Snow
# Invented data. See the lesson for assumptions and interpretation.
treated_before, treated_after = 120, 90
control_before, control_after = 100, 80
treated_change = treated_after - treated_before
control_change = control_after - control_before
print("Treated change (ms):", treated_change)
print("Control change (ms):", control_change)
print("Difference in changes (ms):", treated_change - control_change)
