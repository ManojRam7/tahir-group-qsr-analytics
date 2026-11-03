"""Create a local psql script. Run after generation; execute in psql, not pgAdmin Query Tool."""

from pathlib import Path

import pandas as pd

root = Path(__file__).resolve().parents[1]
manifest = pd.read_csv(root / "sql/postgresql/import_manifest.csv")
lines = ["\\set ON_ERROR_STOP on", "BEGIN;"]
for row in manifest.itertuples():
    csv_path = (root / "data/generated" / f"{row.table}.csv").as_posix().replace("'", "''")
    lines.append(
        f"\\copy qsr.{row.table} ({row.columns}) FROM '{csv_path}' WITH (FORMAT csv, HEADER true)"
    )
lines.append("COMMIT;")
out = root / "output/postgresql/import_local.psql"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(lines) + "\n")
print("Created output/postgresql/import_local.psql; use only with a new empty schema.")
