# Interview defense guide

## Decision 1: use acquired users for the main conversion metric

- **Why:** the business problem starts with traffic/acquisition growth and asks whether those users create value.
- **Denominator:** all acquired users, including those who never produce a usable session.
- **Segmentation:** channel and signup month test whether volume mix explains the topline.
- **Alternative interpretation:** channel conversion can reflect audience, campaign, landing experience, attribution, or observation time.
- **Can conclude:** paid social users have lower observed downstream value in this dataset.
- **Cannot conclude:** paid social is unprofitable or should be cut.
- **Additional data:** spend, marginal CAC, incrementality, attribution windows, contribution margin, campaign/creative.
- **Likely challenge:** “Why not sessions?” Sessions reward repeat visitation and do not match the acquisition decision.

## Decision 2: use a non-strict user funnel

- **Why:** marketplace journeys can skip search or an offer-detail event; reach matters more than one canonical clickstream.
- **Denominator:** acquired users for reach; the immediately prior stage for step conversion.
- **Segmentation:** device diagnoses where transition behavior differs.
- **Alternative interpretation:** missing events or taxonomy errors can look like valid path skipping.
- **Can conclude:** where observed reach falls and which stages merit deeper analysis.
- **Cannot conclude:** that every drop is product failure or that event order is always canonical.
- **Additional data:** event QA, path analysis, page exposure, client/server reconciliation.
- **Likely challenge:** “Why include offer view?” It represents evaluation depth distinct from browsing and provides a candidate activation signal.

## Decision 3: isolate checkout completion at session level

- **Why:** overall device conversion mixes upstream intent with post-checkout execution.
- **Denominator:** sessions with `checkout_start`; numerator is purchase in the same session.
- **Segmentation:** device is directly relevant to interface, performance, and payment options.
- **Alternative interpretation:** mobile users may resume on desktop, have different payment mix, or differ in latent intent.
- **Can conclude:** mobile checkout starters complete less often in observed sessions.
- **Cannot conclude:** the mobile UI causes the entire gap.
- **Additional data:** checkout-step events, error codes, latency, payment method, OS/browser, cross-device identity.
- **Likely challenge:** “Why not user level?” Session level ties the outcome to the checkout episode; user-level reach is retained as a separate view.

## Decision 4: treat channel mix as a composition problem

- **Why:** overall conversion can fall while within-channel performance remains stable if traffic shifts toward a lower-rate channel.
- **Denominator:** users within each channel/cohort.
- **Segmentation:** channel by signup month exposes the changing weights.
- **Alternative interpretation:** later cohorts have less time to convert, campaign targeting changed, or seasonality shifted demand.
- **Can conclude:** acquisition composition contributes to the aggregate movement.
- **Cannot conclude:** it explains every time trend or that channel quality is immutable.
- **Additional data:** fixed-window outcomes, campaign metadata, seasonality history, standardized rates.
- **Likely challenge:** “Is this Simpson’s paradox?” It is the same composition-risk family; the key point is that aggregate movement differs from within-segment interpretation.

## Decision 5: define activation from first-session offer comparison

- **Why:** it is early, behaviorally interpretable, and measured before the later outcome.
- **Denominator:** acquired users with observable first-session behavior.
- **Segmentation:** regression adjusts for channel, device, geography, and cohort.
- **Alternative interpretation:** underlying intent causes both deeper comparison and purchase.
- **Can conclude:** early comparison is a strong predictive signal after measured adjustment.
- **Cannot conclude:** inducing two offer views will increase purchases.
- **Additional data:** experiment assignment, search quality, offer diversity, price dispersion, intent survey.
- **Likely challenge:** “Why two?” It is an interpretable threshold selected for the hypothesis; sensitivity across one, two, and three views should precede operational use.

## Decision 6: use 60-day repeat purchase with eligibility censoring

- **Why:** repeat behavior needs a consistent opportunity window.
- **Denominator:** first-time buyers whose first order occurs at least 60 days before data ends.
- **Segmentation:** channel can reveal whether first-purchase sources differ in durable value.
- **Alternative interpretation:** categories have naturally different replenishment cycles.
- **Can conclude:** 35.4% repeat within 60 days among eligible buyers.
- **Cannot conclude:** long-run retention, loyalty, or profitability.
- **Additional data:** longer history, category cadence, returns, margin, survival analysis.
- **Likely challenge:** “Why 60 days?” It balances marketplace repeat cadence with the six-month observation window; it is a business convention to validate on real data.

## Decision 7: prioritize mobile checkout over category differences

- **Why:** it is close to value, large, measurable, and maps to a testable product surface.
- **Denominator:** checkout-start sessions, not all visits.
- **Segmentation:** pre-specified OS, country, buyer status, category, and payment method in an experiment.
- **Alternative interpretation:** cross-device completion or payment-provider mix may explain part of the gap.
- **Can conclude:** mobile checkout merits focused instrumentation and experimentation.
- **Cannot conclude:** redesigning the entire checkout will necessarily work.
- **Additional data:** step abandonment, field errors, provider outcomes, session replay/qualitative research.
- **Likely challenge:** “Why not acquisition first?” Acquisition economics are missing; checkout has a clearer product-owned mechanism.

## Challenging interview questions and suggested answers

1. **Why is the purchase rate unusually high?** The synthetic marketplace represents registered/acquired users rather than anonymous visits and allows multiple sessions. Absolute rates are not benchmarks; segment relationships and decision logic are the analytical focus.
2. **How did you prevent leakage in activation?** The behavior is restricted to the first session, while purchase is a later user outcome. Same-session purchases can still follow the behavior, which is valid temporally but not causal.
3. **Why logistic regression instead of a predictive model?** The question is whether an interpretable association survives observed mix adjustment, not whether a black-box model maximizes prediction.
4. **How would you explain the odds ratio to a PM?** Holding measured segment mix constant, early comparers have about 1.72 times the odds of purchase; that is not the same as a 72% probability lift.
5. **Why report a p-value for device when the sample is synthetic and large?** It demonstrates uncertainty practice and rules out sampling noise within the constructed population sample, but practical magnitude and bias matter more.
6. **What would make you reverse the mobile recommendation?** Evidence that the gap is mostly cross-device completion, payment mix, tracking loss, or that the feasible improvement is below cost/risk.
7. **Would you cut paid social?** No. I would join spend and contribution margin, use fixed-window value, and test incrementality. Low conversion can still be economical.
8. **How would you handle attribution?** Define an attribution window, compare first/last-touch sensitivity, retain an unattributed group, and prefer incrementality tests for budget decisions.
9. **Why not use revenue as the primary funnel outcome?** Revenue is skewed by repeat orders and basket size. Unique purchase is cleaner for diagnosing first-value creation; revenue per acquired user is a companion metric.
10. **How would you test Simpson’s paradox directly?** Compare crude and standardized rates using fixed channel weights, then inspect within-channel cohort trends and interactions.
11. **What instrumentation would you add?** Checkout step exposure/completion, validation errors, payment method/provider response, latency, cross-device continuation, and cancellation/refund outcomes.
12. **How would you size the experiment?** Use current mobile checkout completion, business minimum detectable lift, two-sided alpha, target power, expected eligibility, and cluster/identity rules; then span complete weekly cycles.
13. **Why intention-to-treat?** It preserves randomization and measures the effect of offering the new experience, avoiding bias from post-assignment engagement.
14. **What is the biggest synthetic-data limitation?** The same author creates and analyzes the behavioral world, so realism and unknown confounding are constrained. The work demonstrates method, not external validity.
15. **What would you do next with one week?** Validate instrumentation, add cross-device and payment data, standardize cohort rates, interview a small set of mobile abandoners, and write the experiment decision memo.

