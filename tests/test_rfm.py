import pandas as pd
import pytest

from analytics.rfm import compute_rfm, segment


@pytest.mark.parametrize(
    "r, f, expected",
    [
        (5, 5, "Champions"), (4, 4, "Champions"),
        (5, 3, "Loyal Customers"), (3, 5, "Loyal Customers"),
        (5, 1, "Potential Loyalists"), (4, 2, "Potential Loyalists"),
        (3, 1, "Need Attention"), (3, 2, "Need Attention"),
        (2, 4, "At Risk"), (1, 3, "At Risk"),
        (1, 1, "Hibernating"), (2, 2, "Hibernating"),
    ],
)
def test_segment_rules(r, f, expected):
    assert segment(r, f) == expected


def test_every_score_combination_gets_a_segment():
    names = {segment(r, f) for r in range(1, 6) for f in range(1, 6)}
    assert names == {"Champions", "Loyal Customers", "Potential Loyalists", "Need Attention", "At Risk", "Hibernating"}


def make_sales():
    """10 customers; customer i orders i times, spends 100*i, last bought i days before the snapshot (reversed)."""
    rows = []
    for i in range(1, 11):
        for k in range(i):
            rows.append({
                "customer_id": i, "invoice_no": f"{i}-{k}",
                "invoice_date": pd.Timestamp("2011-12-01") - pd.Timedelta(days=(11 - i) * 5 + k),
                "revenue": 100.0,
            })
    rows.append({"customer_id": pd.NA, "invoice_no": "anon", "invoice_date": pd.Timestamp("2011-12-01"), "revenue": 999.0})
    df = pd.DataFrame(rows)
    df["customer_id"] = df["customer_id"].astype("Int64")
    return df


def test_rfm_values():
    rfm = compute_rfm(make_sales(), snapshot=pd.Timestamp("2011-12-02")).set_index("customer_id")
    assert len(rfm) == 10  # the anonymous row is excluded
    assert rfm.loc[3, "frequency"] == 3
    assert rfm.loc[3, "monetary"] == 300.0
    assert rfm.loc[10, "recency"] == (pd.Timestamp("2011-12-02") - pd.Timestamp("2011-12-01") + pd.Timedelta(days=5)).days


def test_frequency_counts_invoices_not_lines():
    sales = make_sales()
    extra = sales[sales["customer_id"] == 1].copy()  # a second line on the same invoice
    sales = pd.concat([sales, extra])
    rfm = compute_rfm(sales, snapshot=pd.Timestamp("2011-12-02")).set_index("customer_id")
    assert rfm.loc[1, "frequency"] == 1 and rfm.loc[1, "monetary"] == 200.0


def test_best_and_worst_customers_are_scored_correctly():
    rfm = compute_rfm(make_sales(), snapshot=pd.Timestamp("2011-12-02")).set_index("customer_id")
    assert (rfm.loc[10, ["r", "f", "m"]] == 5).all() and rfm.loc[10, "segment"] == "Champions"
    assert (rfm.loc[1, ["r", "f", "m"]] == 1).all() and rfm.loc[1, "segment"] == "Hibernating"
    assert rfm[["r", "f", "m"]].isin(range(1, 6)).all().all()
