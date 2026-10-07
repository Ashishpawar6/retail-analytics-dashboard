import pandas as pd

from analytics.cohort import cohort_retention


def test_retention_by_cohort_and_month():
    sales = pd.DataFrame({
        "customer_id": pd.array([1, 1, 2, 3], dtype="Int64"),
        "invoice_date": pd.to_datetime(["2011-01-05", "2011-02-05", "2011-01-20", "2011-02-10"]),
    })
    out = cohort_retention(sales).set_index(["cohort", "month_index"])
    assert out.loc[("2011-01", 0), "cohort_size"] == 2
    assert out.loc[("2011-01", 1), "customers"] == 1
    assert out.loc[("2011-01", 1), "retention_pct"] == 50.0
    assert out.loc[("2011-02", 0), "retention_pct"] == 100.0
    assert ("2011-02", 1) not in out.index  # nobody has bought again yet


def test_customers_without_id_are_ignored():
    sales = pd.DataFrame({
        "customer_id": pd.array([1, pd.NA], dtype="Int64"),
        "invoice_date": pd.to_datetime(["2011-01-05", "2011-01-06"]),
    })
    assert cohort_retention(sales)["cohort_size"].iloc[0] == 1
