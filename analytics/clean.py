"""Cleaning rules for the Online Retail data, with a log of what each rule removed.

Every rule is a business decision that changes the numbers, so each one is counted and explained.
"""
from dataclasses import dataclass, field

import pandas as pd

RENAME = {
    "InvoiceNo": "invoice_no", "StockCode": "stock_code", "Description": "description",
    "Quantity": "quantity", "InvoiceDate": "invoice_date", "UnitPrice": "unit_price",
    "CustomerID": "customer_id", "Country": "country",
}

# Codes that are fees or accounting entries rather than products sold.
NON_PRODUCT_CODES = {"POST", "DOT", "M", "C2", "D", "S", "B", "BANK CHARGES", "AMAZONFEE", "CRUK", "PADS"}


@dataclass
class CleanResult:
    sales: pd.DataFrame
    returns: pd.DataFrame
    steps: list[dict] = field(default_factory=list)


def clean(raw: pd.DataFrame) -> CleanResult:
    df = raw.rename(columns=RENAME)[list(RENAME.values())].copy()
    df["invoice_no"] = df["invoice_no"].astype(str)
    df["stock_code"] = df["stock_code"].astype(str)
    steps = [{"step": "Raw rows", "rows": len(df), "reason": "As downloaded"}]

    def log(name: str, removed: int, reason: str) -> None:
        steps.append({"step": name, "rows": -removed, "reason": reason})

    before = len(df)
    df = df.drop_duplicates()
    log("Exact duplicate rows", before - len(df), "Same invoice, product, time and price repeated; likely double entry")

    adjustment = df["invoice_no"].str.startswith("A")
    log("Accounting adjustments", int(adjustment.sum()), "Invoices starting with 'A' are bad-debt adjustments, not sales")
    df = df[~adjustment]

    non_product = df["stock_code"].str.upper().isin(NON_PRODUCT_CODES)
    log("Non-product codes", int(non_product.sum()), "Postage, fees, manual and bank-charge lines are not products")
    df = df[~non_product]

    cancelled = df["invoice_no"].str.startswith("C")
    returns = df[cancelled].copy()
    df = df[~cancelled]
    log("Cancellations moved to returns", int(cancelled.sum()), "Invoices starting with 'C'; analysed separately, not netted into sales")

    bad = (df["quantity"] <= 0) | (df["unit_price"] <= 0)
    log("Zero or negative quantity/price", int(bad.sum()), "Stock write-offs and manual corrections, not customer sales")
    df = df[~bad]

    returns = returns[(returns["quantity"] < 0) & (returns["unit_price"] > 0)].copy()
    returns["quantity"] = -returns["quantity"]  # store returned units as positive numbers

    for frame in (df, returns):
        frame["revenue"] = (frame["quantity"] * frame["unit_price"]).round(2)
        frame["invoice_month"] = frame["invoice_date"].dt.strftime("%Y-%m")
        frame["customer_id"] = frame["customer_id"].astype("Int64")
        frame["description"] = frame["description"].str.strip()

    steps.append({"step": "Clean sales rows", "rows": len(df), "reason": "Used for all revenue analysis"})
    steps.append({"step": "Return rows", "rows": len(returns), "reason": "Used for return analysis"})
    missing_customer = int(df["customer_id"].isna().sum())
    steps.append({
        "step": "Sales rows without a customer ID", "rows": missing_customer,
        "reason": "Kept for revenue totals; excluded from customer analysis (RFM, cohorts, repeat rate)",
    })
    return CleanResult(df.reset_index(drop=True), returns.reset_index(drop=True), steps)
