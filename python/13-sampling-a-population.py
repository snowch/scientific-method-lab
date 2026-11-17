# Copyright © 2026 Christopher Snow
# Constructed population. See the lesson for assumptions and interpretation.
import numpy as np
rng = np.random.default_rng(11)
population = np.concatenate([np.full(800, 40), np.full(200, 140)])
convenience = population[:100]
random_sample = rng.choice(population, size=100, replace=False)
print("Population mean (ms):", population.mean())
print("Desktop-only sample size:", len(convenience))
print("Desktop-only sample mean (ms):", convenience.mean())
print("Mobile requests in desktop-only sample:", int((convenience == 140).sum()))
print("Random sample mean (ms):", random_sample.mean())
print("Slow-group observations in random sample:", int((random_sample == 140).sum()))
