"""Run the analytical pipeline and create publication-ready outputs."""
from __future__ import annotations

import json
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.formula.api as smf
from statsmodels.stats.proportion import proportions_ztest

from src.metrics import STAGES, funnel_summary, user_funnel, wilson_interval

ROOT = Path(__file__).resolve().parents[1]
RAW, PROCESSED, FIGURES = ROOT / "data/raw", ROOT / "data/processed", ROOT / "outputs/figures"


def load_data():
    users = pd.read_csv(RAW / "users.csv", parse_dates=["signup_date"])
    events = pd.read_csv(RAW / "events.csv", parse_dates=["event_timestamp"])
    orders = pd.read_csv(RAW / "orders.csv", parse_dates=["order_timestamp"])
    return users, events, orders


def run():
    PROCESSED.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", context="talk")
    plt.rcParams.update({"figure.dpi": 130, "savefig.bbox": "tight", "axes.titleweight": "bold"})
    users, events, orders = load_data()
    flags = user_funnel(events)
    funnel = funnel_summary(flags)
    profile = users.merge(flags, on="user_id", how="left")
    profile[STAGES] = profile[STAGES].fillna(0).astype(int)
    order_agg = orders.groupby("user_id").agg(orders=("order_id", "nunique"), revenue=("order_value", "sum")).reset_index()
    profile = profile.merge(order_agg, on="user_id", how="left").fillna({"orders": 0, "revenue": 0})
    profile["signup_month"] = profile.signup_date.dt.to_period("M").astype(str)

    # Candidate early behavior is measured in session one. Its outcome begins only
    # after that session ends and uses a complete 14-day window from session start.
    session_bounds = (events.groupby(["user_id", "session_id"]).event_timestamp
                      .agg(first_session_start="min", first_session_end="max").reset_index())
    first_session = (session_bounds.sort_values("first_session_start").drop_duplicates("user_id"))
    first_session_events = events.merge(first_session[["user_id", "session_id"]], on=["user_id", "session_id"])
    early = (first_session_events.groupby("user_id").event_name
             .apply(lambda x: (x == "offer_view").sum()).rename("first_session_offer_views"))
    profile = profile.merge(first_session[["user_id", "first_session_start", "first_session_end"]], on="user_id", how="left")
    profile = profile.merge(early, on="user_id", how="left")
    profile["offer_depth_group"] = pd.cut(profile.first_session_offer_views, [-1, 0, 1, 2, np.inf],
                                           labels=["0", "1", "2", "3+"])

    def segment_table(col):
        out = profile.groupby(col, observed=True).agg(acquired_users=("user_id", "size"), purchasers=("purchase", "sum"),
                                                     revenue=("revenue", "sum")).reset_index()
        out["purchase_rate"] = out.purchasers / out.acquired_users
        out["revenue_per_user"] = out.revenue / out.acquired_users
        out["ci_low"], out["ci_high"] = wilson_interval(out.purchasers, out.acquired_users)
        return out

    channel = segment_table("acquisition_channel").sort_values("purchase_rate", ascending=False)
    device = segment_table("device_type").sort_values("purchase_rate", ascending=False)
    cohort = segment_table("signup_month")

    checkout = (events.assign(is_checkout=events.event_name.eq("checkout_start"), is_purchase=events.event_name.eq("purchase"))
                .groupby(["session_id", "device_type"]).agg(checkout=("is_checkout", "max"), purchase=("is_purchase", "max")).reset_index())
    checkout = checkout[checkout.checkout].groupby("device_type").agg(checkouts=("checkout", "sum"), purchases=("purchase", "sum")).reset_index()
    checkout["completion_rate"] = checkout.purchases / checkout.checkouts
    checkout["ci_low"], checkout["ci_high"] = wilson_interval(checkout.purchases, checkout.checkouts)

    category_sessions = (events.groupby(["session_id", "category"]).event_name.agg(list).reset_index())
    category_sessions["viewed"] = category_sessions.event_name.apply(lambda x: "listing_view" in x or "offer_view" in x)
    category_sessions["purchased"] = category_sessions.event_name.apply(lambda x: "purchase" in x)
    category = category_sessions.groupby("category").agg(exploring_sessions=("viewed", "sum"), purchases=("purchased", "sum")).reset_index()
    category["purchase_per_exploring_session"] = category.purchases / category.exploring_sessions

    outcome_end = events.event_timestamp.max()
    candidate = profile[profile.first_session_start <= outcome_end - pd.Timedelta(days=14)].copy()
    order_window = orders.merge(candidate[["user_id", "first_session_start", "first_session_end"]], on="user_id")
    order_window = order_window[(order_window.order_timestamp > order_window.first_session_end) &
                                (order_window.order_timestamp <= order_window.first_session_start + pd.Timedelta(days=14))]
    future = order_window.groupby("user_id").agg(future_orders_14d=("order_id", "nunique"),
                                                   future_revenue_14d=("order_value", "sum")).reset_index()
    candidate = candidate.merge(future, on="user_id", how="left").fillna({"future_orders_14d": 0, "future_revenue_14d": 0})
    candidate["subsequent_purchase_14d"] = candidate.future_orders_14d.gt(0).astype(int)
    same_session_buyers = set(first_session_events.loc[first_session_events.event_name.eq("purchase"), "user_id"])
    candidate["purchased_first_session"] = candidate.user_id.isin(same_session_buyers)
    activation = candidate.groupby("offer_depth_group", observed=True).agg(
        users=("user_id", "size"), purchasers_14d=("subsequent_purchase_14d", "sum"),
        avg_future_orders_14d=("future_orders_14d", "mean"), avg_future_revenue_14d=("future_revenue_14d", "mean"),
        first_session_purchase_rate=("purchased_first_session", "mean")).reset_index()
    activation["user_share"] = activation.users / activation.users.sum()
    activation["subsequent_purchase_rate_14d"] = activation.purchasers_14d / activation.users
    activation["ci_low"], activation["ci_high"] = wilson_interval(activation.purchasers_14d, activation.users)

    composition = (candidate.groupby(["offer_depth_group", "acquisition_channel"], observed=True).size()
                   .rename("users").reset_index())
    composition["within_depth_share"] = composition.users / composition.groupby("offer_depth_group", observed=True).users.transform("sum")

    # Adjustment checks observed mix; the planted synthetic mechanism and latent
    # intent mean these coefficients cannot be interpreted as causal effects.
    model_df = candidate.copy()
    model = smf.logit("subsequent_purchase_14d ~ C(offer_depth_group, Treatment(reference='0')) + C(acquisition_channel) + C(device_type) + C(country) + C(signup_month)", data=model_df).fit(disp=False)
    dcounts = checkout.set_index("device_type")
    z_stat, p_value = proportions_ztest(dcounts.purchases, dcounts.checkouts)

    # Repeat rate with a consistent 60-day opportunity window.
    ranked = orders.sort_values("order_timestamp").copy()
    ranked["order_number"] = ranked.groupby("user_id").cumcount() + 1
    ranked["next_order"] = ranked.groupby("user_id").order_timestamp.shift(-1)
    first = ranked[(ranked.order_number == 1) & (ranked.order_timestamp <= pd.Timestamp("2024-05-01"))].copy()
    first["repeat_60d"] = first.next_order.le(first.order_timestamp + pd.Timedelta(days=60))
    repeat_rate = first.repeat_60d.mean()

    # Figures
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = ["#173F5F", "#20639B", "#3CAEA3", "#F6D55C", "#ED553B"]
    ax.barh(funnel.stage.str.replace("_", " ").str.title()[::-1], funnel.users[::-1], color=colors[::-1])
    for i, value in enumerate(funnel.users[::-1]): ax.text(value + 300, i, f"{value:,}", va="center", fontsize=10)
    ax.set_title("Most user loss occurs before checkout; completion is the sharper product friction")
    ax.set_xlabel("Unique users"); ax.set_ylabel(""); sns.despine(); fig.savefig(FIGURES / "funnel.png"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5.5))
    plot = channel.sort_values("purchase_rate")
    ax.errorbar(plot.purchase_rate * 100, plot.acquisition_channel.str.replace("_", " ").str.title(),
                xerr=np.vstack([(plot.purchase_rate-plot.ci_low)*100, (plot.ci_high-plot.purchase_rate)*100]), fmt="o", color="#20639B", capsize=4)
    ax.set_title("Paid social adds users, but downstream purchase quality trails every channel")
    ax.set_xlabel("User purchase rate (95% CI)"); ax.set_ylabel(""); sns.despine(); fig.savefig(FIGURES / "channel_conversion.png"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    plot = checkout.sort_values("completion_rate")
    ax.bar(plot.device_type.str.title(), plot.completion_rate * 100, color=["#ED553B", "#3CAEA3"])
    ax.set_title("Mobile users who start checkout are less likely to finish")
    ax.set_ylabel("Checkout completion rate (%)"); ax.set_xlabel(""); sns.despine(); fig.savefig(FIGURES / "device_checkout.png"); plt.close(fig)

    first_order = orders.groupby("user_id").order_timestamp.min().rename("first_order_at")
    monthly_base = profile.merge(first_order, on="user_id", how="left")
    monthly_base = monthly_base[monthly_base.signup_date <= pd.Timestamp("2024-05-31 23:59:59")].copy()
    monthly_base["purchased_30d"] = monthly_base.first_order_at.le(monthly_base.signup_date + pd.Timedelta(days=30))
    monthly = monthly_base.groupby(["signup_month", "acquisition_channel"]).agg(users=("user_id", "size"), rate=("purchased_30d", "mean")).reset_index()
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ch, g in monthly.groupby("acquisition_channel"):
        axes[0].plot(g.signup_month, g.users, marker="o", label=ch.replace("_", " ").title())
        axes[1].plot(g.signup_month, g.rate * 100, marker="o", label=ch.replace("_", " ").title())
    aggregate = monthly_base.groupby("signup_month").purchased_30d.mean()
    axes[1].plot(aggregate.index, aggregate.values * 100, color="#222222", linestyle="--", marker="s", linewidth=2.5, label="Overall")
    axes[0].set_title("Acquisition growth shifts toward paid social"); axes[0].set_ylabel("Acquired users")
    axes[1].set_title("Mix shift depresses aggregate cohort quality"); axes[1].set_ylabel("User purchase rate (%)")
    for ax in axes: ax.tick_params(axis="x", rotation=35); ax.set_xlabel("")
    axes[0].legend(fontsize=8, frameon=False); axes[1].legend(fontsize=8, frameon=False); sns.despine(); fig.savefig(FIGURES / "cohort_mix.png"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    x = np.arange(len(activation))
    rates = activation.subsequent_purchase_rate_14d * 100
    ax.errorbar(x, rates,
                yerr=np.vstack([(activation.subsequent_purchase_rate_14d-activation.ci_low)*100,
                                (activation.ci_high-activation.subsequent_purchase_rate_14d)*100]),
                fmt="o", markersize=10, linewidth=2, capsize=5, color="#20639B")
    labels = [f"{g} {'view' if str(g) == '1' else 'views'}\n(n={n:,})"
              for g, n in zip(activation.offer_depth_group, activation.users)]
    ax.set_xticks(x, labels)
    ax.set_title("Deeper first-session offer exploration is associated with more subsequent 14-day purchasing")
    ax.set_ylabel("Subsequent purchase rate (95% CI)"); ax.set_xlabel("First-session offer views")
    sns.despine(); fig.savefig(FIGURES / "early_offer_depth.png"); plt.close(fig)

    for name, frame in {"funnel": funnel, "channel_metrics": channel, "device_metrics": device,
                        "checkout_completion": checkout, "cohort_metrics": cohort, "category_metrics": category,
                        "early_offer_depth_metrics": activation,
                        "early_offer_depth_channel_mix": composition}.items():
        frame.to_csv(PROCESSED / f"{name}.csv", index=False)
    model_summary = pd.DataFrame({"term": model.params.index, "odds_ratio": np.exp(model.params.values),
                                  "ci_low": np.exp(model.conf_int()[0].values), "ci_high": np.exp(model.conf_int()[1].values),
                                  "p_value": model.pvalues.values})
    model_summary.to_csv(PROCESSED / "early_offer_depth_logit.csv", index=False)

    paid = channel.set_index("acquisition_channel").loc["paid_social"]
    direct = channel.set_index("acquisition_channel").loc["direct"]
    mobile = dcounts.loc["mobile"]
    desktop = dcounts.loc["desktop"]
    summary = {
        "users": len(users), "events": len(events), "orders": len(orders),
        "purchasers": int(profile.purchase.sum()), "purchase_rate": float(profile.purchase.mean()),
        "checkout_users": int(funnel.loc[funnel.stage == "checkout_start", "users"].iloc[0]),
        "checkout_completion_user": float(funnel.loc[funnel.stage == "purchase", "users"].iloc[0] / funnel.loc[funnel.stage == "checkout_start", "users"].iloc[0]),
        "paid_social_users": int(paid.acquired_users), "paid_social_purchase_rate": float(paid.purchase_rate),
        "direct_purchase_rate": float(direct.purchase_rate), "paid_social_revenue_per_user": float(paid.revenue_per_user),
        "mobile_checkout_completion": float(mobile.purchases/mobile.checkouts),
        "desktop_checkout_completion": float(desktop.purchases/desktop.checkouts), "device_test_p": float(p_value),
        "activation_eligible_users_14d": int(len(candidate)),
        "activation_immature_excluded": int(profile.first_session_start.notna().sum() - len(candidate)),
        "activation_no_observed_session_excluded": int(profile.first_session_start.isna().sum()),
        "activation_same_session_buyers_excluded_from_outcome": int(candidate.purchased_first_session.sum()),
        "offer_depth_groups": {str(r.offer_depth_group): {"users": int(r.users), "user_share": float(r.user_share),
            "subsequent_purchase_rate_14d": float(r.subsequent_purchase_rate_14d), "ci_low": float(r.ci_low),
            "ci_high": float(r.ci_high)} for _, r in activation.iterrows()},
        "offer_depth_adjusted_odds_ratios": {row.term: {"odds_ratio": float(row.odds_ratio), "ci_low": float(row.ci_low),
            "ci_high": float(row.ci_high), "p_value": float(row.p_value)} for _, row in model_summary.iterrows()
            if "offer_depth_group" in row.term},
        "repeat_purchase_rate_60d": float(repeat_rate),
    }
    (PROCESSED / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))

