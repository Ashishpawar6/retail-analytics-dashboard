from analytics.clean import clean


def step(result, name):
    return next(s for s in result.steps if s["step"] == name)


def test_each_rule_removes_the_right_rows(raw):
    result = clean(raw)
    assert step(result, "Exact duplicate rows")["rows"] == -1
    assert step(result, "Accounting adjustments")["rows"] == -1
    assert step(result, "Non-product codes")["rows"] == -1
    assert step(result, "Cancellations moved to returns")["rows"] == -1
    assert step(result, "Zero or negative quantity/price")["rows"] == -2


def test_clean_sales_contains_only_real_sales(raw):
    sales = clean(raw).sales
    assert len(sales) == 6
    assert (sales["quantity"] > 0).all() and (sales["unit_price"] > 0).all()
    assert not sales["invoice_no"].str.startswith(("C", "A")).any()
    assert "POST" not in set(sales["stock_code"])


def test_cancellations_become_positive_returns(raw):
    returns = clean(raw).returns
    assert len(returns) == 1
    row = returns.iloc[0]
    assert row["quantity"] == 1 and row["revenue"] == 5.0 and row["invoice_no"] == "C1006"


def test_revenue_and_month_are_derived(raw):
    sales = clean(raw).sales
    first = sales[(sales["invoice_no"] == "1001") & (sales["stock_code"] == "A1")].iloc[0]
    assert first["revenue"] == 10.0 and first["invoice_month"] == "2011-01"


def test_missing_customers_are_kept_but_counted(raw):
    result = clean(raw)
    assert result.sales["customer_id"].isna().sum() == 1
    assert step(result, "Sales rows without a customer ID")["rows"] == 1


def test_step_log_reconciles_with_the_output(raw):
    result = clean(raw)
    start = step(result, "Raw rows")["rows"]
    removed = sum(-s["rows"] for s in result.steps if s["rows"] < 0)
    assert start - removed == len(result.sales)
    assert start == len(raw)
