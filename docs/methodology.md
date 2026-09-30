# Methodology

## Analytical frame

The unit of analysis changes with the decision. Acquisition quality uses acquired users; product-step diagnosis uses sessions; retention uses eligible first-time buyers. This avoids a single denominator being stretched across unlike questions.

The user funnel is `session start → listing view → offer view → checkout start → purchase`. It is non-strict because marketplace paths can legitimately skip search or offer-detail events. The funnel answers reach; session-level transitions answer localized friction.

## Data-generating process

`src/generate_data.py` creates users first, then their sessions and ordered events, then orders only when checkout completes. Channel, device, country, category, latent intent, prior purchase, and random noise influence behavior. Channel mix changes over calendar time. The fixed seed is `20250308`.

These mechanics make the tables internally coherent while preserving overlap between groups. They are hidden from the main analytical narrative to keep the exercise discovery-led.

## Uncertainty and modeling

Wilson 95% intervals accompany segment purchase rates because they remain stable for proportions. A two-sample proportion test quantifies the precision of the device completion difference. The activation logistic regression adjusts for observed channel, device, country, and signup-month mix. Odds ratios are reported as associations; neither the test nor the regression establishes causality.

## Cohort maturity

Conversion comparisons use a fixed 30-day outcome window where cohort maturity matters. Repeat purchase includes only first orders on or before 1 May, leaving a complete 60-day follow-up before the dataset ends. Users without enough observation are excluded from that retention denominator rather than counted as non-repeaters.

## Quality checks

The reproducibility command validates non-empty outputs from every SQL file, checks record counts and figure artifacts, and executes the notebook in place. Public figures and README values are generated from `data/processed/summary.json` and companion CSVs.

