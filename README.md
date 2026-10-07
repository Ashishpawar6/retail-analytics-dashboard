# Retail Sales and Customer Analytics

An end-to-end data analysis project on **real data**: 540,000 transactions from a UK online retailer. It cleans messy data with documented rules, answers business questions with **SQL**, segments customers with **RFM**, measures **cohort retention**, and presents everything in an interactive **Streamlit dashboard** plus a written findings report.

**Stack:** Python, pandas, SQL (SQLite), Streamlit, Plotly, pytest.

> **Start here:** [reports/FINDINGS.md](reports/FINDINGS.md) has the business findings and recommendations.

## Headline findings

- September to November produced **35%** of revenue in 3 of 13 months; November was about **2.1x** a typical spring/summer month.
- The top 10% of customers generate **61%** of revenue; the 26% of customers in the *Champions* segment generate **66%**.
- **653 "At Risk" customers** (£805k historical spend) have not ordered in ~5 months, which makes them a win-back target.
- Two top-selling products by gross revenue were **almost entirely returned**, so ranking must use net revenue.
- **14.7% of revenue has no customer ID**, which limits customer analysis.

## Dataset

[UCI Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail): 541,909 invoice lines, 1 Dec 2010 to 9 Dec 2011, 38 countries. It is public and needs no login; the pipeline downloads it for you (about 24 MB, not stored in this repo).

## Setup and run (To view Dashboard)

```bash
cd retail-analytics-dashboard         # the folder you cloned or downloaded
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

python -m analytics.pipeline          # downloads, cleans, builds data/retail.db (about 30 s the first time)
streamlit run app/dashboard.py        # starts the dashboard
pytest                                # 33 tests
```

### Viewing the dashboard

`streamlit run app/dashboard.py` starts a local web server and normally opens your browser at **http://localhost:8501**. If the browser does not open, paste that address into it. Press `Ctrl+C` in the terminal to stop the app.

Run `python -m analytics.pipeline` once before the first launch: the database is not stored in the repo, and the dashboard shows an error asking you to build it if it is missing.

No account or login is needed for any of this.

## What is in the dashboard

| Tab | Contents |
|---|---|
| Overview | KPIs, monthly revenue, top products, weekday/hour heatmap. Filter by date range and country. |
| Customers | RFM segment table and revenue split, spend-vs-orders scatter, revenue concentration, repeat rate, cohort retention heatmap |
| Countries | Revenue by country (UK can be excluded to see the rest) |
| Returns | Top products by *net* revenue, highest return rates |
| Data quality | Every cleaning step with the number of rows removed and why |

## Project structure

```
analytics/
  download.py   fetch the dataset
  clean.py      cleaning rules with a log of rows removed per rule
  rfm.py        Recency/Frequency/Monetary scoring and segments
  cohort.py     cohort retention matrix
  db.py         build the SQLite database, run .sql files
  pipeline.py   runs everything (CLI)
sql/            7 commented queries (CTEs, window functions: LAG, NTILE, SUM OVER)
app/dashboard.py  Streamlit app
tests/          33 tests
reports/FINDINGS.md  business findings
```

## Cleaning decisions

| Rule | Rows | Why |
|---|---|---|
| Exact duplicates | 5,268 | Likely double entry |
| Accounting adjustments (`A...` invoices) | 3 | Bad-debt entries, not sales |
| Non-product codes (postage, fees, bank charges) | 2,907 | Not products sold |
| Cancellations (`C...` invoices) | 8,668 | **Moved to a separate returns table**, not netted into sales |
| Zero or negative quantity/price | 2,495 | Stock write-offs and corrections |
| Missing customer ID | 131,418 kept | Kept for revenue; excluded from customer analysis |

## SQL queries

`sql/` holds one commented query per business question: monthly revenue with month-over-month growth (`LAG`), top products by net revenue (CTEs and `JOIN`), country share (`SUM() OVER ()`), customer concentration (`NTILE`), repeat-customer rate, return rates, and a weekday/hour heatmap. Tests check each query against a tiny dataset with hand-computed answers.

## Design decisions and limitations

- **Cancellations are separated, not netted.** Netting would hide return behaviour and distort order counts. Returns are analysed on their own, and net revenue is shown where it matters.
- **SQLite** keeps the project zero-setup. The SQL is standard and works on MySQL or PostgreSQL with small changes (for example the date functions).
- **Dashboard filters apply to the Overview tab only.** RFM and cohorts need each customer's full history, so filtering rows would make them wrong.
- **December 2011 is a partial month** (ends 9 Dec); the dashboard and report say so wherever it matters.
- The analysis is descriptive, covers one retailer and one year, and does not prove causes. See the limitations section in the findings report.
- The dashboard was tested headlessly with Streamlit's test framework (it renders without errors on the full dataset), but there are no screenshots in this repo yet.
- Not deployed anywhere; it runs locally.
