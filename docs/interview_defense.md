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
- **Likely challenge:** “Why include offer view?” It represents evaluation depth distinct from browsing and provides a candidate early behavioral signal.

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

## Decision 5: evaluate offer depth as a candidate early signal

- **Why:** offer depth is early and interpretable, but the analysis should not assume where a useful threshold lies.
- **Denominator:** 35,911 users with an observed first session and a complete 14-day follow-up window.
- **Outcome:** purchase after session one ends and within 14 days of its start; same-session purchases do not qualify.
- **Grouping:** 0, 1, 2, and 3+ views; the upper tail is pooled because only 4.8% reach 3+.
- **Segmentation:** regression adjusts for channel, device, geography, and signup cohort.
- **Alternative interpretation:** persistent purchase intent causes both deeper comparison and later purchase.
- **Can conclude:** rates rise gradually with depth and the association survives measured adjustment.
- **Cannot conclude:** two views are a unique threshold or that inducing views will cause purchases.
- **Additional data:** randomized exposure, comparison-module engagement, offer relevance/diversity, price dispersion, and intent research.
- **Likely challenge:** “Did 2+ survive?” It remains a practical segmentation, but not a validated activation cutoff; 2 and 3+ rates are similar and their intervals overlap.

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

1. **Why was 2+ originally chosen?** It was an interpretable hypothesis for comparison behavior, not a data-derived optimum. The sensitivity analysis was required before treating it as more than a candidate split.
2. **Why test 0, 1, 2, and 3+ separately?** It reveals whether there is a step change or a gradient. Pooling 3+ stabilizes a small upper tail while preserving the important depth pattern.
3. **Did the 2+ threshold survive?** Only as a convenient segmentation. Rates rise from 6.1% to 6.8%, 7.9%, and 8.2%; there is no unique cliff, and 2 versus 3+ is not clearly different.
4. **Why exclude purchases in the first session?** They can occur after the measured clicks but belong to the same journey and are directly influenced by offer depth in the generator. A later outcome provides cleaner temporal ordering.
5. **Why use 14 days?** It is long enough to capture near-term return behavior while retaining most cohorts and staying relevant to an activation hypothesis. It was specified before inspecting the refined result.
6. **How were immature users handled?** Users whose first session began within 14 days of collection ending were excluded, not labeled non-purchasers; 3,974 observed users were removed on that basis.
7. **Does exploration cause later purchase?** No. The analysis shows temporal association. Randomization is needed to estimate whether an intervention that facilitates comparison changes purchase behavior.
8. **Could intent explain both?** Yes. That is the leading alternative explanation, and the generator explicitly contains persistent latent intent.
9. **What does synthetic construction imply?** Recovering a planted association validates the workflow, not the mechanism. The data cannot establish external validity or a real operational activation metric.
10. **When would you call this an activation metric?** After replicated observational stability, clear instrumentation, incremental experimental impact, and evidence that optimizing it does not harm downstream value or marketplace balance.
11. **How would you validate it in a real product?** Instrument first-session comparison, replicate by cohort and market, run qualitative research, then randomize a low-friction decision-support feature and analyze 14-day purchase by assignment.
12. **Why logistic regression?** The question is whether an interpretable association survives observed mix adjustment, not whether a complex model maximizes prediction.
13. **How do you explain the adjusted result?** Relative to zero views and holding measured mix constant, the odds ratios are 1.10, 1.26, and 1.30 for 1, 2, and 3+ views. They are not causal lifts.
14. **Would you cut paid social?** No. I would join spend and contribution margin, use fixed-window value, and test incrementality. Low conversion can still be economical.
15. **Why intention-to-treat in the proposed experiment?** It preserves randomization and measures the effect of offering comparison support, rather than selecting users who choose to engage with it.

