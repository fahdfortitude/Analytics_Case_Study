"""Execute every SQL file and verify public outputs against computed results."""
from pathlib import Path
import json
import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
con = duckdb.connect()
con.execute(f"CREATE VIEW users AS SELECT * FROM read_csv_auto('{(ROOT/'data/raw/users.csv').as_posix()}')")
con.execute(f"CREATE VIEW events AS SELECT * FROM read_csv_auto('{(ROOT/'data/raw/events.csv').as_posix()}')")
con.execute(f"CREATE VIEW orders AS SELECT * FROM read_csv_auto('{(ROOT/'data/raw/orders.csv').as_posix()}')")
for path in sorted((ROOT / "sql").glob("*.sql")):
    result = con.execute(path.read_text(encoding="utf-8")).fetchdf()
    assert len(result) > 0, f"No rows from {path.name}"
    print(f"PASS {path.name}: {len(result)} row(s)")
summary = json.loads((ROOT / "data/processed/summary.json").read_text())
for figure in ["funnel.png", "channel_conversion.png", "device_checkout.png", "cohort_mix.png", "early_offer_depth.png"]:
    assert (ROOT / "outputs/figures" / figure).stat().st_size > 10_000
assert summary["users"] == 40_000
assert 200_000 < summary["events"] < 1_000_000
assert summary["activation_eligible_users_14d"] == sum(v["users"] for v in summary["offer_depth_groups"].values())
assert summary["activation_eligible_users_14d"] + summary["activation_immature_excluded"] + summary["activation_no_observed_session_excluded"] == summary["users"]
events = con.execute("SELECT * FROM events").fetchdf()
orders = con.execute("SELECT * FROM orders").fetchdf()
first_bounds = (events.groupby(["user_id", "session_id"]).event_timestamp.agg(["min", "max"]).reset_index()
                .sort_values("min").drop_duplicates("user_id"))
eligible = first_bounds[first_bounds["min"] <= events.event_timestamp.max() - pd.Timedelta(days=14)]
window = orders.merge(eligible[["user_id", "min", "max"]], on="user_id")
qualified = window[(window.order_timestamp > window["max"]) &
                   (window.order_timestamp <= window["min"] + pd.Timedelta(days=14))]
assert (qualified.order_timestamp > qualified["max"]).all()
assert (qualified.order_timestamp <= qualified["min"] + pd.Timedelta(days=14)).all()
first_session_keys = eligible[["user_id", "session_id"]]
same_session = events.merge(first_session_keys, on=["user_id", "session_id"])
assert same_session.loc[same_session.event_name.eq("purchase"), "user_id"].nunique() == summary["activation_same_session_buyers_excluded_from_outcome"]
print("PASS outputs and summary checks")

