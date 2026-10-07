"""RFM customer segmentation: Recency, Frequency, Monetary value."""
import pandas as pd


def segment(r: int, f: int) -> str:
    """Map recency and frequency scores (1 = worst, 5 = best) to a named segment."""
    if r >= 4:
        return "Champions" if f >= 4 else ("Loyal Customers" if f == 3 else "Potential Loyalists")
    if r == 3:
        return "Loyal Customers" if f >= 3 else "Need Attention"
    return "At Risk" if f >= 3 else "Hibernating"


def _score(values: pd.Series, higher_is_better: bool) -> pd.Series:
    """Quintile score 1-5. Ranking first breaks ties deterministically so every bucket is filled."""
    ranked = values.rank(method="first", ascending=higher_is_better)
    return pd.qcut(ranked, 5, labels=[1, 2, 3, 4, 5]).astype(int)


def compute_rfm(sales: pd.DataFrame, snapshot: pd.Timestamp | None = None) -> pd.DataFrame:
    known = sales[sales["customer_id"].notna()]
    snapshot = snapshot or (known["invoice_date"].max().normalize() + pd.Timedelta(days=1))
    rfm = known.groupby("customer_id").agg(
        last_purchase=("invoice_date", "max"),
        frequency=("invoice_no", "nunique"),
        monetary=("revenue", "sum"),
    )
    rfm["recency"] = (snapshot - rfm["last_purchase"].dt.normalize()).dt.days
    rfm["r"] = _score(rfm["recency"], higher_is_better=False)  # fewer days since last purchase is better
    rfm["f"] = _score(rfm["frequency"], higher_is_better=True)
    rfm["m"] = _score(rfm["monetary"], higher_is_better=True)
    rfm["segment"] = [segment(r, f) for r, f in zip(rfm["r"], rfm["f"])]
    rfm["monetary"] = rfm["monetary"].round(2)
    return rfm.reset_index().drop(columns="last_purchase")
