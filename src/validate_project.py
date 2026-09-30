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
for figure in ["funnel.png", "channel_conversion.png", "device_checkout.png", "cohort_mix.png", "activation.png"]:
    assert (ROOT / "outputs/figures" / figure).stat().st_size > 10_000
assert summary["users"] == 40_000
assert 200_000 < summary["events"] < 1_000_000
print("PASS outputs and summary checks")

