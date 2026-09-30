"""Shared metric definitions used by the notebook and validation scripts."""
from __future__ import annotations

import numpy as np
import pandas as pd


STAGES = ["session_start", "listing_view", "offer_view", "checkout_start", "purchase"]


def wilson_interval(successes: pd.Series, totals: pd.Series, z: float = 1.96):
    p = successes / totals
    denom = 1 + z**2 / totals
    centre = (p + z**2 / (2 * totals)) / denom
    spread = z * np.sqrt((p * (1 - p) + z**2 / (4 * totals)) / totals) / denom
    return centre - spread, centre + spread


def user_funnel(events: pd.DataFrame) -> pd.DataFrame:
    flags = (events.assign(value=1).pivot_table(index="user_id", columns="event_name", values="value",
                                                aggfunc="max", fill_value=0))
    for stage in STAGES:
        if stage not in flags:
            flags[stage] = 0
    return flags[STAGES].reset_index()


def funnel_summary(flags: pd.DataFrame) -> pd.DataFrame:
    counts = flags[STAGES].sum().astype(int)
    result = pd.DataFrame({"stage": STAGES, "users": counts.values})
    result["share_of_acquired_users"] = result.users / result.users.iloc[0]
    result["step_conversion"] = result.users / result.users.shift(1)
    result.loc[0, "step_conversion"] = 1.0
    return result

