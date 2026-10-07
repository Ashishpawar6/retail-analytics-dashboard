"""Interactive retail analytics dashboard.

    streamlit run app/dashboard.py

Reads the SQLite database built by `python -m analytics.pipeline` (path in $RETAIL_DB).
"""
import os
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from analytics.db import run_sql_file

DB_PATH = Path(os.getenv("RETAIL_DB", "data/retail.db"))

st.set_page_config(page_title="Retail Analytics", page_icon="📊", layout="wide")

if not DB_PATH.exists():
    st.error(f"Database not found at `{DB_PATH}`. Build it first with `python -m analytics.pipeline`.")
    st.stop()


def query(sql: str, params: tuple = ()) -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(sql, conn, params=params)


@st.cache_data(show_spinner=False)
def saved_query(name: str) -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as conn:
        return run_sql_file(conn, name)


@st.cache_data(show_spinner=False)
def table(name: str) -> pd.DataFrame:
    return query(f"SELECT * FROM {name}")


@st.cache_data(show_spinner=False)
def filtered(sql_template: str, start: str, end: str, countries: tuple) -> pd.DataFrame:
    """Run a query containing {where}; the filter is applied with bound parameters."""
    marks = ",".join("?" * len(countries))
    where = f"date(invoice_date) BETWEEN ? AND ? AND country IN ({marks})"
    return query(sql_template.format(where=where), (start, end, *countries))


bounds = query("SELECT date(MIN(invoice_date)) AS lo, date(MAX(invoice_date)) AS hi FROM sales").iloc[0]
all_countries = query("SELECT DISTINCT country FROM sales ORDER BY country")["country"].tolist()

with st.sidebar:
    st.header("Filters")
    date_range = st.date_input(
        "Date range", (pd.to_datetime(bounds.lo), pd.to_datetime(bounds.hi)),
        min_value=pd.to_datetime(bounds.lo), max_value=pd.to_datetime(bounds.hi),
    )
    chosen = st.multiselect("Countries", all_countries, default=all_countries)
    st.caption("Filters apply to the Overview tab. Customer, return and data-quality tabs use all data.")

if len(date_range) != 2 or not chosen:
    st.info("Pick a date range (start and end) and at least one country.")
    st.stop()
start, end = (d.strftime("%Y-%m-%d") for d in date_range)
countries = tuple(chosen)

st.title("📊 Retail Sales & Customer Analytics")
st.caption("UCI Online Retail dataset (UK online gift retailer, Dec 2010 - Dec 2011). December 2011 covers 1-9 Dec only.")

overview, customers_tab, countries_tab, returns_tab, quality = st.tabs(
    ["Overview", "Customers", "Countries", "Returns", "Data quality"]
)

# ---------------------------------------------------------------- Overview
with overview:
    kpi = filtered(
        "SELECT COALESCE(SUM(revenue),0) AS revenue, COUNT(DISTINCT invoice_no) AS orders, "
        "COUNT(DISTINCT customer_id) AS customers FROM sales WHERE {where}", start, end, countries,
    ).iloc[0]
    ret = filtered("SELECT COALESCE(SUM(revenue),0) AS value FROM returns WHERE {where}", start, end, countries).iloc[0]["value"]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Gross revenue", f"£{kpi.revenue:,.0f}")
    c2.metric("Returns", f"£{ret:,.0f}", f"{100 * ret / kpi.revenue:.1f}% of revenue" if kpi.revenue else None, delta_color="off")
    c3.metric("Orders", f"{int(kpi.orders):,}")
    c4.metric("Customers (with ID)", f"{int(kpi.customers):,}")
    c5.metric("Avg order value", f"£{kpi.revenue / kpi.orders:,.0f}" if kpi.orders else "-")

    monthly = filtered(
        "SELECT invoice_month AS month, SUM(revenue) AS revenue, COUNT(DISTINCT invoice_no) AS orders "
        "FROM sales WHERE {where} GROUP BY invoice_month ORDER BY invoice_month", start, end, countries,
    )
    if monthly.empty:
        st.warning("No sales for this selection.")
    else:
        st.subheader("Monthly revenue")
        st.plotly_chart(px.bar(monthly, x="month", y="revenue", labels={"revenue": "Revenue (£)", "month": ""}), width="stretch")

        left, right = st.columns(2)
        with left:
            st.subheader("Top 10 products by revenue")
            top = filtered(
                "SELECT MAX(description) AS product, SUM(revenue) AS revenue FROM sales WHERE {where} "
                "GROUP BY stock_code ORDER BY revenue DESC LIMIT 10", start, end, countries,
            )
            fig = px.bar(top.iloc[::-1], x="revenue", y="product", orientation="h", labels={"revenue": "Revenue (£)", "product": ""})
            st.plotly_chart(fig, width="stretch")
            st.caption("Gross revenue. See the Returns tab: some top products were largely returned.")
        with right:
            st.subheader("When customers buy")
            hours = filtered(
                "SELECT CAST(strftime('%w', invoice_date) AS INTEGER) AS d, CAST(strftime('%H', invoice_date) AS INTEGER) AS hour, "
                "SUM(revenue) AS revenue FROM sales WHERE {where} GROUP BY d, hour", start, end, countries,
            )
            names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
            heat = hours.pivot(index="d", columns="hour", values="revenue").reindex(range(7)).fillna(0)
            heat.index = names
            st.plotly_chart(px.imshow(heat, aspect="auto", labels={"x": "Hour", "y": "", "color": "Revenue (£)"}), width="stretch")
            st.caption("No sales are recorded on Saturdays in this dataset.")

# ---------------------------------------------------------------- Customers
with customers_tab:
    rfm = table("rfm")
    st.subheader("RFM segments")
    st.caption("Recency (days since last order), Frequency (number of orders), Monetary (total spend). Scores 1-5, 5 is best.")
    seg = rfm.groupby("segment").agg(
        customers=("customer_id", "count"), revenue=("monetary", "sum"),
        avg_recency_days=("recency", "mean"), avg_orders=("frequency", "mean"),
    ).sort_values("revenue", ascending=False)
    seg["revenue_share_pct"] = 100 * seg["revenue"] / seg["revenue"].sum()
    seg["customer_share_pct"] = 100 * seg["customers"] / seg["customers"].sum()
    left, right = st.columns([3, 2])
    with left:
        st.dataframe(seg.round(1), width="stretch")
    with right:
        st.plotly_chart(px.pie(seg.reset_index(), names="segment", values="revenue", hole=0.45), width="stretch")

    sample = rfm.sample(min(len(rfm), 2000), random_state=1)
    st.plotly_chart(
        px.scatter(sample, x="frequency", y="monetary", color="segment", log_x=True, log_y=True,
                   labels={"frequency": "Orders (log)", "monetary": "Total spend £ (log)"}, opacity=0.6),
        width="stretch",
    )

    st.subheader("Revenue concentration")
    conc = saved_query("04_customer_concentration")
    st.plotly_chart(px.bar(conc, x="decile", y="revenue_share_pct", labels={"decile": "Customer decile (1 = top 10%)", "revenue_share_pct": "Share of revenue (%)"}), width="stretch")

    rep = saved_query("05_repeat_customers").iloc[0]
    st.metric("Repeat customers", f"{rep.repeat_rate_pct}%", f"{int(rep.repeat_customers):,} of {int(rep.customers):,}", delta_color="off")

    st.subheader("Cohort retention")
    st.caption("Of the customers who first bought in a month (rows), the % who bought again k months later (columns).")
    cohort = table("cohort_retention").pivot(index="cohort", columns="month_index", values="retention_pct")
    st.plotly_chart(
        px.imshow(cohort, text_auto=".0f", aspect="auto", color_continuous_scale="Blues",
                  labels={"x": "Months since first purchase", "y": "First-purchase month", "color": "Retention %"}),
        width="stretch",
    )

# ---------------------------------------------------------------- Countries
with countries_tab:
    by_country = saved_query("03_country_revenue")
    exclude_uk = st.toggle("Exclude United Kingdom", value=True)
    shown = by_country[by_country["country"] != "United Kingdom"] if exclude_uk else by_country
    st.plotly_chart(px.bar(shown.head(15), x="country", y="revenue", labels={"revenue": "Revenue (£)", "country": ""}), width="stretch")
    uk = by_country.loc[by_country["country"] == "United Kingdom", "revenue_share_pct"]
    if not uk.empty:
        st.caption(f"The United Kingdom accounts for {uk.iloc[0]:.1f}% of all revenue.")
    st.dataframe(shown, width="stretch", hide_index=True)

# ---------------------------------------------------------------- Returns
with returns_tab:
    st.subheader("Top products by net revenue (sales minus returns)")
    st.dataframe(saved_query("02_top_products"), width="stretch", hide_index=True)
    st.subheader("Highest return rates (products with at least £5,000 sales)")
    st.dataframe(saved_query("06_return_rates"), width="stretch", hide_index=True)

# ---------------------------------------------------------------- Data quality
with quality:
    st.subheader("What the cleaning step removed, and why")
    steps = table("cleaning_steps")
    st.dataframe(steps.rename(columns={"step": "Step", "rows": "Rows", "reason": "Why"}), width="stretch", hide_index=True)
    st.markdown(
        "- Cancellations are **not netted into sales**; they are analysed separately as returns.\n"
        "- Rows without a customer ID are kept for revenue totals but excluded from customer analysis.\n"
        "- December 2011 is a partial month (data ends 9 Dec), so its month-over-month change is not meaningful."
    )
