import pandas as pd
import pytest


def make_raw(price_scale: float = 1.0) -> pd.DataFrame:
    """A small raw dataset (original column names) with every kind of row the cleaner must handle."""
    rows = [
        # InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country
        ("1001", "A1", "WIDGET", 2, "2011-01-05 10:00:00", 5.0, 1.0, "United Kingdom"),
        ("1001", "B1", "GADGET", 1, "2011-01-05 10:00:00", 20.0, 1.0, "United Kingdom"),
        ("1002", "A1", "WIDGET", 3, "2011-01-20 11:30:00", 5.0, 2.0, "United Kingdom"),
        ("1003", "A1", "WIDGET", 1, "2011-02-10 09:15:00", 5.0, 1.0, "United Kingdom"),
        ("1004", "B1", "GADGET", 2, "2011-02-15 14:00:00", 20.0, 3.0, "Germany"),
        ("1004", "B1", "GADGET", 2, "2011-02-15 14:00:00", 20.0, 3.0, "Germany"),      # exact duplicate
        ("1005", "A1", "WIDGET", 1, "2011-02-16 15:45:00", 5.0, None, "United Kingdom"),  # no customer ID
        ("C1006", "A1", "WIDGET", -1, "2011-02-20 16:00:00", 5.0, 1.0, "United Kingdom"),  # cancellation
        ("1007", "POST", "POSTAGE", 1, "2011-02-21 10:00:00", 15.0, 1.0, "United Kingdom"),  # not a product
        ("A1008", "B", "Adjust bad debt", 1, "2011-02-22 10:00:00", 100.0, None, "United Kingdom"),
        ("1009", "A1", "WIDGET", 0, "2011-02-23 10:00:00", 5.0, 2.0, "United Kingdom"),   # zero quantity
        ("1010", "A1", "WIDGET", 1, "2011-02-24 10:00:00", 0.0, 2.0, "United Kingdom"),   # zero price
    ]
    df = pd.DataFrame(rows, columns=["InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID", "Country"])
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["UnitPrice"] = df["UnitPrice"] * price_scale
    return df


@pytest.fixture
def raw():
    return make_raw()
