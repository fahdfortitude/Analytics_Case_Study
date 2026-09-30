# Methodology

## Analytical frame

The unit of analysis changes with the decision. Acquisition quality uses acquired users; product-step diagnosis uses sessions; retention uses eligible first-time buyers. This avoids a single denominator being stretched across unlike questions.

The user funnel is `session start → listing view → offer view → checkout start → purchase`. It is non-strict because marketplace paths can legitimately skip search or offer-detail events. The funnel answers reach; session-level transitions answer localized friction.

## Data-generating process

`src/generate_data.py` creates users first, then their sessions and ordered events, then orders only when checkout completes. Channel, device, country, category, latent intent, prior purchase, and random noise influence behavior. Channel mix changes over calendar time. The fixed seed is `20250308`.

These mechanics make the tables internally coherent while preserving overlap between groups. They are hidden from the main analytical narrative to keep the exercise discovery-led.

## Early offer-depth outcome

The candidate early behavior is the number of `offer_view` events in a user's first observed session, grouped as 0, 1, 2, and 3+. The groups preserve useful depth while keeping the sparse upper tail interpretable: only 4.8% of eligible users have 3+ views.

The outcome is at least one purchase strictly **after the first session ends** and no later than 14 days after that session starts. The denominator contains users whose first session begins at least 14 days before the final observed event. This leaves 35,911 eligible users; 3,974 users with an observed but immature first session and 115 users without an observed session are excluded. Users who purchase in session one remain eligible, but that purchase does not satisfy the subsequent-purchase outcome. This temporal separation removes reverse ordering and the generator's direct same-session path, although it does not eliminate common-cause bias.

Wilson 95% intervals accompany group rates. A logistic regression compares each depth group with zero views while adjusting for acquisition channel, device, country, and signup month. These variables address plausible observed composition differences without turning the analysis into a prediction exercise. Odds ratios remain associations, not causal effects.

## Synthetic-construction limitation

Inspection of `src/generate_data.py` shows that offer depth contributes directly to same-session checkout probability. The refined outcome excludes same-session purchases, so that direct mechanical relationship is not counted. However, persistent latent intent influences both first-session exploration and behavior in later sessions. The subsequent association is therefore partly induced by construction. Recovering it demonstrates the workflow used to evaluate a candidate activation behavior; it is not empirical validation of a real-world behavioral mechanism or threshold.

Temporal ordering improves the question from “did users who explored purchase at any time?” to “did exploration precede a later purchase?” It still cannot establish that encouraging exploration would change outcomes, because underlying intent can cause both.

## Other uncertainty and modeling

A two-sample proportion test quantifies the precision of the device completion difference. As elsewhere, practical magnitude and alternative explanations take priority over statistical significance.

## Cohort maturity

Conversion comparisons use a fixed 30-day outcome window where cohort maturity matters. Repeat purchase includes only first orders on or before 1 May, leaving a complete 60-day follow-up before the dataset ends. Users without enough observation are excluded from that retention denominator rather than counted as non-repeaters.

## Quality checks

The reproducibility command validates non-empty outputs from every SQL file, checks record counts and figure artifacts, and executes the notebook in place. Public figures and README values are generated from `data/processed/summary.json` and companion CSVs.

