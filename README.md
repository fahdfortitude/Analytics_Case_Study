# Marketplace Funnel & Activation Analysis

## Executive summary

Marketplace acquisition grew, but downstream growth did not keep pace. Analysis of a six-month synthetic dataset (40,000 users, 468,253 events, and 25,472 orders) identifies two different problems hidden inside the topline trend.

First, acquisition mix shifted toward paid social. That channel supplied 9,603 users but converted 22.7% to purchase, compared with 51.6% for direct traffic. Its revenue per acquired user was £22.97. The aggregate conversion decline is therefore partly a composition effect—not evidence that every channel or the whole product deteriorated.

Second, users who reach checkout are materially less likely to finish on mobile: 66.2% session-level completion versus 84.4% on desktop. This is the clearest product-friction signal because it appears after users have expressed purchase intent. The evidence does not prove that the interface causes the gap; payment mix, context, and device performance remain plausible alternatives.

The recommended first action remains a mobile checkout diagnostic. In parallel, acquisition reviews should pair volume with 30-day purchase rate and revenue per acquired user. A maturity-controlled sensitivity analysis finds that subsequent 14-day purchasing rises gradually with first-session offer depth—from 6.1% at zero views to 8.2% at 3+ views. This supports deeper exploration as an early behavioral signal, but not `2+ views` as a uniquely validated activation threshold.

![User funnel](outputs/figures/funnel.png)

## Business question

Why is increased traffic not translating into proportional marketplace growth, and where should the product team intervene?

The investigation separates three possibilities: lower-quality acquisition, broad product deterioration, and localized funnel friction.

## Dataset

This project uses **synthetic data generated specifically for this portfolio case study**. It contains no proprietary, client, or real-user information. The generator uses a fixed seed and models behavior sequentially: acquisition affects latent intent and device mix; users create sessions; sessions produce exploration; exploration can lead to checkout; completed checkouts create orders and influence later behavior.

| Table | Grain | Rows | Selected fields |
|---|---:|---:|---|
| `users` | One row per acquired user | 40,000 | signup date, country, channel, device |
| `events` | One row per behavioral event | 468,253 | session, timestamp, event, listing, category |
| `orders` | One row per completed order | 25,472 | value, category, first-purchase flag |

The observation period is 1 January–30 June 2024. The generator's embedded mechanics are intentionally not documented here; the analytical claims below come from the same observable tables available to an analyst.

## Metric definitions

| Metric | Definition | Why this denominator |
|---|---|---|
| User purchase rate | Unique purchasers / acquired users | Measures downstream acquisition quality without rewarding repeat orders |
| Exploration rate | Users with a listing or offer view / acquired users | Tests whether acquired users engage with supply |
| Checkout-start rate | Users starting checkout / acquired users | Captures purchase intent reached |
| Checkout completion | Purchasers / checkout starters | Isolates the post-checkout loss point |
| Revenue per acquired user | Revenue / acquired users | Connects channel volume and quality to value |
| 60-day repeat rate | Buyers with a second order within 60 days / first-time buyers with a full window | Avoids penalizing recent buyers with incomplete follow-up |
| Candidate early signal | First-session offer depth: 0, 1, 2, or 3+ views | Tested against purchases after that session and within a complete 14-day window |

The main funnel is non-strict and user-level: a user counts as reaching a stage if they reach it at least once. Session-level analysis is used where the question concerns checkout completion in a particular visit.

## Analytical approach

1. Establish a metric contract before segmenting.
2. Locate funnel loss at both user and session level.
3. Separate acquisition volume from purchase quality and revenue.
4. Compare channel, device, country, category, and signup cohorts.
5. test whether aggregate cohort movement is explained by channel mix.
6. Evaluate offer-depth sensitivity against a temporally separated 14-day outcome, then adjust for observed mix.
7. Translate findings into prioritized decisions and a falsifiable experiment.

SQL builds the reusable funnel, cohort, retention, and segmentation views. Python handles uncertainty intervals, regression, visualization, and cross-checks. Full assumptions are in [methodology.md](docs/methodology.md).

## Key findings

### 1. Acquisition growth is increasingly concentrated in a lower-quality channel

**Finding.** Paid social contributes substantial volume but has the lowest downstream purchase rate.

**Evidence.** Its 22.7% user purchase rate is less than half direct traffic's 51.6%. The acquisition mix moves toward paid social across later cohorts while aggregate cohort conversion declines.

![Channel conversion](outputs/figures/channel_conversion.png)

![Cohort mix](outputs/figures/cohort_mix.png)

**Interpretation.** The portfolio-level decline is partly mix-driven. A channel can be effective on marginal acquisition cost despite a lower conversion rate, but cost data is unavailable here.

**Product implication.** Do not optimize acquisition on signups alone. Report 30-day purchase rate and revenue per acquired user by channel and cohort; join spend before making budget changes.

### 2. Mobile checkout completion is the highest-priority product friction

**Finding.** The device gap widens after checkout begins.

**Evidence.** 66.2% of mobile checkout sessions complete versus 84.4% on desktop. The difference is precise in this dataset (two-proportion test p < 0.001), but precision does not remove selection bias.

![Device checkout](outputs/figures/device_checkout.png)

**Interpretation.** Form complexity, payment support, page performance, or interruption could explain the gap. Mobile users may also differ in unobserved intent.

**Product implication.** Instrument checkout steps and failure reasons, review performance and payment-method coverage, then test a smaller mobile checkout change.

### 3. Deeper early exploration predicts later purchasing, without a unique threshold

**Finding.** Subsequent purchase rates rise across 0, 1, 2, and 3+ first-session offer views, but the pattern is gradual rather than a sharp step at two.

**Evidence.** Among 35,911 users with a full follow-up window, purchase **after the first session and within 14 days of its start** rises from 6.1% (0 views; n=16,657) to 6.8% (1; n=12,548), 7.9% (2; n=4,968), and 8.2% (3+; n=1,738). First-session purchases do not count toward this outcome. The adjusted odds ratios versus zero views are 1.10, 1.26, and 1.30 after controlling for channel, device, country, and signup month.

![Subsequent purchasing by first-session offer depth](outputs/figures/early_offer_depth.png)

**Interpretation.** The original `2+` split remains usable as a concise candidate segmentation because the largest incremental separation occurs by two views, but it is not an empirically unique threshold: rates for 2 and 3+ overlap. Comparison may build confidence, or high-intent users may naturally explore more. The synthetic generator also gives persistent latent intent a role in both behaviors; recovering that planted association is not real-world validation.

**Product implication.** Use offer depth as an early engagement marker for diagnosis. Test decision support that makes comparison easier; do not force extra clicks or operationalize an activation metric until randomized evidence shows that the intervention changes downstream outcomes.

### 4. Retention is meaningful, but not the first intervention point

Among first-time buyers with a complete 60-day follow-up window, 35.4% make a second purchase. This is useful as a guardrail and long-term outcome, but the largest actionable gap occurs before the first purchase.

## Recommended actions

### Priority 1 — diagnose and test mobile checkout friction

- **Evidence:** 18.2 percentage-point mobile completion gap among checkout sessions.
- **Expected mechanism:** fewer form and payment failures allow existing purchase intent to complete.
- **Metric:** completed purchase per mobile checkout starter.
- **Success test:** statistically and practically meaningful lift without lower order value, higher refunds, or increased payment failures.

### Priority 2 — change acquisition quality reporting

- **Evidence:** paid social growth coincides with a 22.7% purchase rate and £22.97 revenue per acquired user.
- **Expected mechanism:** teams optimize for users likely to create value, not raw traffic.
- **Metric:** channel-level 30-day purchase rate and contribution margin per acquired user once spend is joined.
- **Success test:** stable or improved qualified acquisition at an acceptable marginal cost.

### Priority 3 — test decision support around offer exploration

- **Evidence:** a modest, monotonic adjusted association with subsequent 14-day purchase; no unique threshold.
- **Expected mechanism:** relevant comparisons may reduce uncertainty and support choice without adding friction.
- **Metric:** purchase within 14 days of first session, with guardrails for time-to-checkout and seller concentration.
- **Success test:** intention-to-treat lift among eligible first-session users, not higher offer-view counts alone.

**What should not trigger an immediate product change:** category conversion differences, the offer-depth association, and the paid-social rate alone. Each lacks at least one critical input—supply context, causal identification, or acquisition cost.

## Proposed experiment: first-session offer comparison support

- **Hypothesis:** helping new users compare relevant offers will reduce decision uncertainty and increase subsequent 14-day purchasing.
- **Treatment:** a lightweight comparison module after the first offer view, showing a small set of relevant alternatives and decision-relevant attributes without requiring extra navigation.
- **Control:** current offer-view experience.
- **Randomization unit:** user, assigned on the first eligible offer view and held consistently across devices where identity permits.
- **Eligibility:** newly acquired users in their first session who view one offer, excluding employees, bots, and users already assigned to conflicting tests.
- **Primary metric:** purchase after the assignment session and within 14 days of session start.
- **Analysis population:** all assigned eligible users by original assignment (intention to treat), regardless of whether treatment users engage with the module.
- **Guardrails:** checkout-start rate, time to checkout, bounce rate, page latency, order value, refund/cancellation rate, and seller/category concentration.
- **Expected mechanism:** clearer comparison reduces uncertainty; offer views themselves are not the success metric.
- **Major risks:** added choice overload, slower pages, substitution toward a narrow seller set, or treatment contamination across devices.

No experiment result is claimed. Before launch, use the baseline 14-day purchase rate and a product-owned minimum detectable effect to set sample size and duration; enrollment and follow-up must cover complete weekly cycles plus the full outcome window.

## Limitations

- Synthetic behavior can illustrate analytical reasoning but cannot validate a real marketplace mechanism. In the generator, persistent latent intent influences both exploration and later purchase opportunities; offer depth also directly affects same-session checkout probability, which is why same-session purchases are excluded from the candidate-signal outcome.
- Channel spend, margin, refunds, seller quality, price competitiveness, inventory, payment method, OS, and page-performance data are absent.
- Device and behavioral segments are observational; adjusted models only address measured confounders.
- The six-month window limits seasonal inference and longer-term retention.
- Multiple sessions can cross devices in a real product; this simplified dataset assigns a primary device.

## Repository structure

```text
├── README.md
├── run_all.py
├── requirements.txt
├── data/{raw,processed}/
├── notebooks/marketplace_analysis.ipynb
├── sql/
├── src/{generate_data.py,metrics.py,run_analysis.py,build_notebook.py,validate_project.py}
├── outputs/figures/
└── docs/{methodology.md,interview_defense.md}
```

## Reproducing the analysis

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python run_all.py
```

`run_all.py` regenerates the raw data with a fixed seed, recomputes processed outputs and figures, executes every SQL query, rebuilds the notebook, and executes it top to bottom. On a typical laptop, allow roughly one minute.

