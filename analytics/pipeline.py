"""Download -> clean -> segment -> build the SQLite database.

    python -m analytics.pipeline
"""
import argparse
from pathlib import Path

import pandas as pd

from analytics.clean import clean
from analytics.cohort import cohort_retention
from analytics.db import build_database
from analytics.download import download
from analytics.rfm import compute_rfm

INTERIM = Path("data/interim/online_retail_raw.csv")


def load_raw() -> pd.DataFrame:
    """Read the Excel file once, then reuse a CSV copy (Excel parsing takes ~25 s)."""
    if INTERIM.exists():
        return pd.read_csv(INTERIM, dtype={"InvoiceNo": str, "StockCode": str}, parse_dates=["InvoiceDate"])
    xlsx = download()
    raw = pd.read_excel(xlsx, dtype={"InvoiceNo": str, "StockCode": str})
    INTERIM.parent.mkdir(parents=True, exist_ok=True)
    raw.to_csv(INTERIM, index=False)
    return raw


def run(raw: pd.DataFrame, db_path: Path) -> dict:
    result = clean(raw)
    rfm = compute_rfm(result.sales)
    cohorts = cohort_retention(result.sales)
    build_database(
        db_path,
        {
            "sales": result.sales,
            "returns": result.returns,
            "rfm": rfm,
            "cohort_retention": cohorts,
            "cleaning_steps": pd.DataFrame(result.steps),
        },
    )
    return {"sales": len(result.sales), "returns": len(result.returns), "customers": len(rfm)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="data/retail.db")
    args = parser.parse_args()
    summary = run(load_raw(), Path(args.db))
    print(f"Built {args.db}: {summary['sales']:,} sales rows, {summary['returns']:,} return rows, {summary['customers']:,} customers")
