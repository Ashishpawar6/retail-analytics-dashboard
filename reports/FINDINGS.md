# Findings: Retail Sales and Customer Analytics

**Data:** UCI Online Retail, a UK-based online gift retailer selling mostly to wholesale and trade customers. 1 Dec 2010 to 9 Dec 2011.
**After cleaning:** 522,568 sales lines, 19,773 orders, £10.25M gross sales, 4,334 identified customers, 8,668 return lines worth £0.48M.
All figures below come from the SQL in `sql/` and the RFM and cohort code in `analytics/`; the dashboard shows the same numbers.

## Summary

1. **Revenue is strongly seasonal.** September to November produced **35%** of the 13-month revenue in just 3 of the 13 months. November (£1.45M) was about **2.1x** the average month from March to August (£0.68M).
2. **A small group of customers drives the business.** The top 10% of customers account for **61%** of revenue, and the *Champions* RFM segment (26% of customers) for **66%**.
3. **There is a clear win-back opportunity.** 653 *At Risk* customers (15% of customers) have spent £805k historically but have not ordered for about 5 months on average.
4. **Gross revenue can mislead.** Two of the top-10 products by gross revenue were almost entirely returned. Net revenue changes the ranking.
5. **The UK is 85% of revenue,** but a few export markets have very large orders, which suggests wholesale buyers.

## 1. Seasonality

| Period | Revenue | Share of 13-month total |
|---|---|---|
| Sep - Nov 2011 (3 months) | £3.58M | 35.0% |
| Mar - Aug 2011 (6 months, average per month) | £0.68M | n/a |
| Nov 2011 alone | £1.45M | 14.2% |

Month-over-month growth was +42% in September and +32% in November. December 2011 shows -58%, but that is an artefact: the data ends on 9 December, so only 9 days are included.

**Recommendation:** plan stock, staffing and marketing spend for a ramp starting in September.

## 2. Customer concentration and RFM segments

Revenue share by customer decile (identified customers only): the top decile is **61.4%**, the top two deciles **74.6%**, and the bottom five deciles together just **7.8%**.

| Segment | Customers | Share of customers | Share of revenue | Avg days since last order | Avg orders |
|---|---|---|---|---|---|
| Champions | 1,119 | 25.8% | 66.0% | 13 | 10.0 |
| Loyal Customers | 828 | 19.1% | 15.5% | 38 | 3.7 |
| At Risk | 653 | 15.1% | 9.2% | 151 | 3.4 |
| Hibernating | 1,081 | 24.9% | 5.9% | 217 | 1.1 |
| Need Attention | 344 | 7.9% | 1.8% | 53 | 1.1 |
| Potential Loyalists | 309 | 7.1% | 1.5% | 19 | 1.2 |

65.3% of identified customers ordered more than once (4.2 orders per customer on average).

**Recommendations:**
- Protect Champions (early access, account management): losing a few of them costs more than losing many small customers.
- Run a targeted win-back campaign for *At Risk* customers; they were repeat buyers (3.4 orders on average), so they are a better target than one-time Hibernating customers.
- Move *Potential Loyalists* to a second and third order with an offer soon after their first purchase.

## 3. Retention by cohort

Of customers whose first purchase fell in January to October 2011, roughly **15-24%** bought again in the following month. The December 2010 group retained far better (**36.5%** in month 1, and between 32% and 40% in each of the next five months).

**Caveat:** the December 2010 "cohort" is not truly new customers. The dataset starts in December 2010, so that group includes customers who had bought before the data begins. Their higher retention reflects an established customer base, not a successful onboarding. The November 2011 cohort's month-1 value (11.1%) is also understated because December 2011 is incomplete.

## 4. Gross revenue versus net revenue

| Product | Gross sales | Returned | Return rate |
|---|---|---|---|
| 23843 PAPER CRAFT, LITTLE BIRDIE | £168,470 | £168,470 | 100% |
| 23166 MEDIUM CERAMIC TOP STORAGE JAR | £81,701 | £77,480 | 94.8% |

Both are single huge orders (80,995 and 74,215 units) that were cancelled. Ranked by gross revenue they would be the #2 and #6 products. By **net** revenue the top product is the REGENCY CAKESTAND 3 TIER (£164k net), followed by PARTY BUNTING and WHITE HANGING HEART T-LIGHT HOLDER (about £98k each).

**Recommendation:** report net revenue, and investigate why very large orders are placed and cancelled (credit checks, data-entry errors or order confirmation).

## 5. Geography

The United Kingdom contributes **85.1%** of revenue. The next markets are the Netherlands (2.8%), EIRE (2.6%), Germany (2.0%) and France (1.8%).

Average order value shows very different customers:

| Market | Orders | Revenue | Revenue per order |
|---|---|---|---|
| United Kingdom | 17,901 | £8.73M | £487 |
| Netherlands | 93 | £284k | £3,053 |
| Australia | 56 | £138k | £2,466 |
| Germany | 443 | £205k | £464 |

The Netherlands and Australia buy rarely but in very large quantities, which looks like wholesale buying. These accounts are good candidates for dedicated account management.

## 6. When customers buy

- **No sales are recorded on Saturdays.**
- Thursday is the strongest day (£2.13M, 20.8% of revenue); Sunday is the weakest (£0.80M, 7.8%).
- **74%** of revenue falls between 10:00 and 15:59.

**Recommendation:** schedule campaigns and customer-service coverage around weekday late mornings and early afternoons.

## 7. Data quality issues worth acting on

- **14.7% of revenue (25% of sales lines) has no customer ID.** That revenue cannot be tied to any customer, which limits retention and segmentation work. Capturing an identifier at checkout would be a high-value fix.
- 5,268 exact duplicate rows were removed, which suggests double entry in the source system.

## Limitations of this analysis

- One retailer and roughly one year of data; seasonality cannot be separated from a growth trend with only a single year.
- The RFM quintile thresholds are relative to this customer base, and ties are broken by row order, so scores near a boundary are somewhat arbitrary.
- Returns are matched to products, not to the original orders, so a return may refer to a sale from before the data starts.
- All findings are descriptive: they show *what* happened, not *why*. Recommendations are hypotheses to test, not proven causes.
