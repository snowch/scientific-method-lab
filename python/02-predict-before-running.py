# Copyright © 2026 Christopher Snow
# Authored model. See the lesson for assumptions and interpretation.
import numpy as np
import matplotlib.pyplot as plt
repeat_fraction = np.linspace(0, 1, 6)
repeat_model = 40 * repeat_fraction
setup_model = np.full(6, 15.0)
print("Repeat fractions:", repeat_fraction.round(1))
print("Repeat model saving (ms):", repeat_model)
print("Setup model saving (ms):", setup_model)
plt.plot(repeat_fraction, repeat_model, "o-", label="Repeated-key explanation")
plt.plot(repeat_fraction, setup_model, "s--", label="Fixed-setup explanation")
plt.xlabel("Fraction of repeated keys"); plt.ylabel("Predicted saving (ms)")
plt.legend(); plt.tight_layout()
