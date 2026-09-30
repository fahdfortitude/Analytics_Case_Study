"""Generate reproducible, behaviorally coherent marketplace data."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 20250308
CHANNELS = np.array(["direct", "organic_search", "referral", "paid_search", "paid_social"])
COUNTRIES = np.array(["UK", "Germany", "France", "Spain", "Netherlands"])
CATEGORIES = np.array(["electronics", "home", "fashion", "collectibles", "services"])


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def generate(output_dir: str | Path = "data/raw", n_users: int = 40_000) -> dict[str, int]:
    rng = np.random.default_rng(SEED)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    start = pd.Timestamp("2024-01-01")
    end = pd.Timestamp("2024-06-30 23:59:59")
    days = (end.normalize() - start).days + 1

    # Acquisition mix shifts toward paid social over time, creating volume growth
    # without hard-coding an outcome column.
    signup_day = np.floor(days * rng.beta(1.32, 1.0, n_users)).astype(int).clip(0, days - 1)
    month_ix = (signup_day // 30).clip(0, 5)
    channel_probs = np.array([
        [.25, .28, .15, .22, .10], [.24, .27, .14, .21, .14],
        [.23, .25, .13, .20, .19], [.21, .24, .12, .19, .24],
        [.19, .23, .11, .18, .29], [.17, .21, .10, .17, .35],
    ])
    channel = np.array([rng.choice(CHANNELS, p=channel_probs[m]) for m in month_ix])
    device_p_mobile = np.where(channel == "paid_social", .84, np.where(channel == "referral", .69, .58))
    device = np.where(rng.random(n_users) < device_p_mobile, "mobile", "desktop")
    country = rng.choice(COUNTRIES, n_users, p=[.28, .22, .19, .17, .14])
    signup = start + pd.to_timedelta(signup_day, unit="D") + pd.to_timedelta(rng.integers(0, 86400, n_users), unit="s")
    user_ids = np.array([f"U{i:06d}" for i in range(1, n_users + 1)])
    users = pd.DataFrame({"user_id": user_ids, "signup_date": signup, "country": country,
                          "acquisition_channel": channel, "device_type": device})

    channel_intent = {"direct": .58, "organic_search": .35, "referral": .28,
                      "paid_search": .18, "paid_social": -.48}
    country_effect = {"UK": .10, "Germany": .04, "France": 0, "Spain": -.04, "Netherlands": .06}
    category_probs = {
        "direct": [.24, .22, .20, .17, .17], "organic_search": [.22, .22, .18, .20, .18],
        "referral": [.20, .21, .22, .18, .19], "paid_search": [.22, .24, .19, .19, .16],
        "paid_social": [.14, .14, .39, .24, .09],
    }
    category_value = {"electronics": 116, "home": 74, "fashion": 49, "collectibles": 86, "services": 62}
    category_intent = {"electronics": .18, "home": .10, "fashion": -.28, "collectibles": -.18, "services": .12}

    events: list[tuple] = []
    orders: list[tuple] = []
    order_no = 1
    for i, uid in enumerate(user_ids):
        latent = rng.normal() + channel_intent[channel[i]] + country_effect[country[i]]
        max_days = max(1, (end - signup[i]).days + 1)
        session_rate = np.exp(.36 + .34 * latent) * min(1, max_days / 80)
        n_sessions = int(np.clip(1 + rng.poisson(session_rate), 1, 15))
        extra_offsets = (rng.integers(1, max_days, max(0, n_sessions - 1))
                         if max_days > 1 else np.array([], dtype=int))
        offsets = np.sort(np.unique(np.r_[0, extra_offsets]))
        prior_purchase = False
        first_session_offer_depth = 0
        for s_idx, off in enumerate(offsets):
            ts = signup[i] + pd.Timedelta(days=int(off), seconds=int(rng.integers(0, 72000)))
            if ts > end:
                continue
            sid = f"{uid}_S{s_idx + 1:02d}"
            category = rng.choice(CATEGORIES, p=category_probs[channel[i]])
            events.append((uid, sid, ts, "session_start", None, category, device[i], channel[i]))
            explore_score = latent + category_intent[category] * .25 + rng.normal(scale=.8)
            if rng.random() < sigmoid(.95 + .45 * explore_score):
                events.append((uid, sid, ts + pd.Timedelta(seconds=int(rng.integers(15, 150))), "search", None, category, device[i], channel[i]))
            n_views = int(np.clip(rng.poisson(1.8 + .55 * sigmoid(explore_score)), 0, 6))
            for v in range(n_views):
                lid = f"L{rng.integers(1, 12001):05d}"
                events.append((uid, sid, ts + pd.Timedelta(seconds=180 + 75 * v), "listing_view", lid, category, device[i], channel[i]))
            offer_depth = int(np.clip(rng.poisson(.45 + .62 * sigmoid(explore_score)), 0, 4))
            if s_idx == 0:
                first_session_offer_depth = offer_depth
            for v in range(offer_depth):
                lid = f"L{rng.integers(1, 12001):05d}"
                events.append((uid, sid, ts + pd.Timedelta(seconds=500 + 90 * v), "offer_view", lid, category, device[i], channel[i]))
            checkout_score = -2.02 + .92 * latent + .38 * min(n_views, 3) + .52 * min(offer_depth, 2) + category_intent[category]
            checkout = rng.random() < sigmoid(checkout_score)
            if checkout:
                checkout_ts = ts + pd.Timedelta(seconds=int(rng.integers(850, 2400)))
                events.append((uid, sid, checkout_ts, "checkout_start", None, category, device[i], channel[i]))
                # Mobile friction occurs after checkout; channel effects operate mainly via intent/mix.
                completion_score = 1.18 + .40 * latent + category_intent[category] - (.92 if device[i] == "mobile" else 0)
                if prior_purchase:
                    completion_score += .34
                if rng.random() < sigmoid(completion_score):
                    purchase_ts = checkout_ts + pd.Timedelta(seconds=int(rng.integers(45, 600)))
                    events.append((uid, sid, purchase_ts, "purchase", None, category, device[i], channel[i]))
                    value = round(float(rng.lognormal(np.log(category_value[category]), .42)), 2)
                    orders.append((f"O{order_no:07d}", uid, purchase_ts, value, category, not prior_purchase, sid))
                    order_no += 1
                    prior_purchase = True

    event_cols = ["user_id", "session_id", "event_timestamp", "event_name", "listing_id", "category", "device_type", "acquisition_channel"]
    order_cols = ["order_id", "user_id", "order_timestamp", "order_value", "category", "first_purchase", "session_id"]
    event_df = pd.DataFrame(events, columns=event_cols).sort_values("event_timestamp")
    order_df = pd.DataFrame(orders, columns=order_cols).sort_values("order_timestamp")
    users.to_csv(output / "users.csv", index=False, date_format="%Y-%m-%d %H:%M:%S")
    event_df.to_csv(output / "events.csv", index=False, date_format="%Y-%m-%d %H:%M:%S")
    order_df.to_csv(output / "orders.csv", index=False, date_format="%Y-%m-%d %H:%M:%S")
    return {"users": len(users), "events": len(event_df), "orders": len(order_df)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="data/raw")
    parser.add_argument("--users", type=int, default=40_000)
    args = parser.parse_args()
    print(generate(args.output_dir, args.users))

