"""Cohort retention: of the customers who first bought in month X, how many came back k months later?"""
import pandas as pd


def cohort_retention(sales: pd.DataFrame) -> pd.DataFrame:
    known = sales[sales["customer_id"].notna()].copy()
    known["month"] = known["invoice_date"].dt.to_period("M")
    known["cohort"] = known.groupby("customer_id")["month"].transform("min")
    known["month_index"] = (known["month"] - known["cohort"]).apply(lambda offset: offset.n)

    active = known.groupby(["cohort", "month_index"])["customer_id"].nunique().rename("customers").reset_index()
    sizes = active[active["month_index"] == 0].set_index("cohort")["customers"].rename("cohort_size")
    active = active.join(sizes, on="cohort")
    active["retention_pct"] = (100 * active["customers"] / active["cohort_size"]).round(1)
    active["cohort"] = active["cohort"].astype(str)
    return active
