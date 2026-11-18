"""Literal edits learners can make in the prepared editor on each lesson route."""
# Each variant begins at the published code, with cumulative changes where a
# lesson asks for another change on top of the first one.
EDITS = [
    [((('minimum_reduction_pct = 20', 'minimum_reduction_pct = 10'),), ('Pairs meeting 10%: 5',))],
    [((('np.full(6, 15.0)', 'np.full(6, 30.0)'),), ('Setup model saving (ms): [30. 30. 30. 30. 30. 30.]',))],
    [((('[1000, 1000, 500, 500]', '[1000, 1000, 1000, 1000]'),), ('ms_per_request', '0.052'))],
    [
        ((('resolution_ms = 10', 'resolution_ms = 1'),), ('Displayed (ms): [11. 12. 13. 14. 21. 22.]',)),
        ((('resolution_ms = 10', 'resolution_ms = 1'), ('offset_ms = 5', 'offset_ms = np.array([0, 1, 2, 3, 4, 5])')), ('With offset (ms): [11 13 15 17 25 27]',)),
    ],
    [((('prediction = 40 * repeat_fraction', 'prediction = 40 * repeat_fraction + 12'),), ('Observed minus predicted (ms): [ 0. -1.  0. -1.  0.]',))],
    [((('treated_before, treated_after = 120, 90', 'treated_before, treated_after = 120, 100'),), ('Treated change (ms): -20', 'Difference in changes (ms): 0'))],
    [
        ((('np.random.default_rng(42)', 'np.random.default_rng(7)'),), ('Mean position by treatment:', 'background_ms')),
        ((('np.random.default_rng(42)', 'np.random.default_rng(19)'),), ('Mean position by treatment:', 'background_ms')),
    ],
    [((('pairs["b_minus_a"] =', 'pairs.loc[pairs.machine == "M3", ["a_ms", "b_ms"]] += 100\npairs["b_minus_a"] ='),), ('b_minus_a', 'M3'))],
    [((('readings_per_session = 20', 'readings_per_session = 200'),), ('Sessions, readings/session: (6, 200)', 'SE across session means (ms):'))],
    [((('"on_ms": [110, 60]', '"on_ms": [60, 60]'),), ('Difference of effects (ms): 0',))],
    [((('10, 10, 10, 10, 210', '10, 10, 10, 10, 110'),), ('Means (ms): 50.0 30.0', 'Medians (ms): 50.0 10.0', 'Longest observed time (ms): 52 110'))],
    [((('population_sd_ms = 15', 'population_sd_ms = 30'),), ('n=1000', 'SD=', 'SE='))],
    [((('convenience = population[:100]', 'convenience = population[:500]'),), ('Desktop-only sample size: 500', 'Mobile requests in desktop-only sample: 0', 'Desktop-only sample mean (ms): 40.0'))],
    [((('labels = np.repeat(["A", "B"], 6)', 'labels = np.tile(["A", "B"], 6)'),), ("Run labels: ['A' 'B' 'A' 'B'", 'Mean time for A (ms):', 'Mean time for B (ms):'))],
    [((('Mean among recorded times (ms)', 'Mean treating timeouts as zero (ms)'), ('data.elapsed_ms.mean()', 'data.elapsed_ms.fillna(0).mean()')), ('Mean treating timeouts as zero (ms):', "'timeout': 2"))],
    [((('confidence_level = 0.95', 'confidence_level = 0.99'),), ('99% t interval for population mean (ms):', 'Observed range (ms): 97 104'))],
    [((('confidence_level = 0.95', 'confidence_level = 0.99'),), ('Covering true mean:', 'Confidence level: 99%'))],
    [
        ((('bootstrap_method = "basic"', 'bootstrap_method = "percentile"'),), ('95% percentile bootstrap interval (ms):', 'Mean B-minus-A (ms): -8.5')),
        ((('bootstrap_method = "basic"', 'bootstrap_method = "BCa"'),), ('95% BCa bootstrap interval (ms):', 'Mean B-minus-A (ms): -8.5')),
    ],
    [((('log_ratio = np.log', 'b = b * 0.9\nlog_ratio = np.log'),), ('95% t interval for A/B ratio:', 'Ratio needed for a 20% reduction: 1.25'))],
    [
        ((('effect_ms, sd_ms = 3, 10', 'effect_ms, sd_ms = 0, 10'),), ('simulated detection fraction=',)),
        ((('effect_ms, sd_ms = 3, 10', 'effect_ms, sd_ms = 1, 10'),), ('simulated detection fraction=',)),
        ((('effect_ms, sd_ms = 3, 10', 'effect_ms, sd_ms = 6, 10'),), ('simulated detection fraction=',)),
    ],
    [
        ((('observed_mean = -5.0', 'observed_mean = -1.0'),), ('Simulated null experiments: 5000',)),
        ((('observed_mean = -5.0', 'observed_mean = -1.0'), ('noise_sd_ms = 10', 'noise_sd_ms = 20')), ('Simulated null experiments: 5000',)),
    ],
    [((('72, 119', '90, 140'),), ('Exact assignment patterns: 256', 'Two-sided permutation p-value:'))],
    [((('effect_ms = .2', 'effect_ms = .02'),), ('n=30000', 'ms p='))],
    [
        ((('m = 20', 'm = 1'),), ('Independent-test formula: 0.05',)),
        ((('m = 20', 'm = 50'),), ('Independent-test formula: 0.923',)),
    ],
    [
        ((('looks = [20, 40, 60, 80, 100]', 'looks = [100]'),), ('Planned observation counts: [100]',)),
        ((('looks = [20, 40, 60, 80, 100]', 'looks = list(range(10, 101, 10))'),), ('Planned observation counts: [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]',)),
    ],
    [((('rng.normal(0, 1, len(load))', 'rng.normal(0, 8, len(load))'),), ('Observed correlation:',))],
    [((('fit_count = 10', 'fit_count = 5'),), ('Prediction at size 10 (ms):', 'Authored time at size 10 (ms): 220'))],
    [((('data["reduction_pct"] =', 'data = pd.concat([data, data[data.environment == "phone"]], ignore_index=True)\ndata["reduction_pct"] ='),), ('Pooled mean reduction (%):', 'Mean reduction (%) by environment:'))],
    [((('include_set_construction = False', 'include_set_construction = True'),), ('B includes set construction', 'Paired blocks share one runtime'))],
    [((('minimum_reduction_pct = 20', 'minimum_reduction_pct = 10'),), ('10% reduction requires A/B >= 1.111.', 'INPUT: INVENTED starter data'))],
]
