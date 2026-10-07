import sqlite3

import pytest

from analytics.clean import clean
from analytics.db import build_database, run_sql_file
from tests.conftest import make_raw


def make_db(tmp_path, price_scale=1.0, name="test.db"):
    result = clean(make_raw(price_scale))
    path = tmp_path / name
    build_database(path, {"sales": result.sales, "returns": result.returns})
    return sqlite3.connect(path)


@pytest.fixture
def conn(tmp_path):
    return make_db(tmp_path)


def test_monthly_revenue_and_growth(conn):
    df = run_sql_file(conn, "01_monthly_revenue").set_index("month")
    assert df.loc["2011-01", "revenue"] == 45.0
    assert df.loc["2011-02", "revenue"] == 50.0
    assert (df.loc["2011-01", "orders"], df.loc["2011-02", "orders"]) == (2, 3)
    assert df.loc["2011-02", "customers"] == 2  # the sale without a customer ID is not counted
    assert df.loc["2011-02", "mom_growth_pct"] == 11.1
    assert df["mom_growth_pct"].isna().iloc[0]  # the first month has nothing to compare with


def test_top_products_are_ranked_by_net_revenue(conn):
    df = run_sql_file(conn, "02_top_products")
    assert list(df["stock_code"]) == ["B1", "A1"]
    a1 = df.set_index("stock_code").loc["A1"]
    assert (a1.gross_revenue, a1.return_value, a1.net_revenue) == (35.0, 5.0, 30.0)


def test_country_share(conn):
    df = run_sql_file(conn, "03_country_revenue").set_index("country")
    assert df.loc["United Kingdom", "revenue"] == 55.0 and df.loc["Germany", "revenue"] == 40.0
    assert df["revenue_share_pct"].sum() == pytest.approx(100, abs=0.02)


def test_customer_concentration(conn):
    df = run_sql_file(conn, "04_customer_concentration")
    assert list(df["customers"]) == [1, 1, 1]
    assert df["revenue_share_pct"].iloc[0] == 44.4  # customer 3 spent 40 of 90
    assert df["revenue_share_pct"].sum() == pytest.approx(100, abs=0.2)


def test_repeat_customers(conn):
    row = run_sql_file(conn, "05_repeat_customers").iloc[0]
    assert (row.customers, row.repeat_customers, row.repeat_rate_pct) == (3, 1, 33.3)


def test_return_rates_use_the_minimum_sales_threshold(conn, tmp_path):
    assert run_sql_file(conn, "06_return_rates").empty  # tiny sales are below the 5,000 threshold
    big = make_db(tmp_path, price_scale=1000, name="big.db")
    df = run_sql_file(big, "06_return_rates").set_index("stock_code")
    assert df.loc["A1", "return_rate_pct"] == 14.3 and df.loc["B1", "return_rate_pct"] == 0.0
    assert df.index[0] == "A1"  # highest rate first


def test_weekday_hour_totals_match_total_revenue(conn):
    df = run_sql_file(conn, "07_weekday_hour")
    assert df["revenue"].sum() == 95.0
    assert df["hour"].between(0, 23).all() and df["weekday_num"].between(0, 6).all()
