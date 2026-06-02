# E-Commerce Customer & Revenue Analytics Platform
## Business Insights Report

**Generated:** June 02, 2026
**Report Period:** Full Dataset Analysis
**Analysis Engine:** Python 3 | Pandas | Scikit-learn | SQLite

---

## 1. Executive Summary

This report presents a comprehensive analysis of the e-commerce transaction dataset, covering
customer behaviour, revenue performance, product analysis, geographic distribution, and a
6-month revenue forecast.

| KPI | Value |
|-----|-------|
| **Total Revenue** | £598,799.86 |
| **Total Orders** | 3,748 |
| **Total Customers** | 1,499 |
| **Average Order Value (AOV)** | £159.77 |
| **Revenue per Customer** | £399.47 |
| **Repeat Purchase Rate** | 97.9% |
| **Customer Retention Rate** | 94.2% |
| **Avg Monthly Revenue Growth** | 15.2% |

---

## 2. Key Revenue Findings

- **Total Revenue Generated:** £598,799.86 across 3,748 orders
- **Average Order Value:** £159.77 — opportunity exists to increase basket size via upselling
- **Revenue per Customer:** £399.47 — indicates strong per-customer monetisation
- **Monthly Growth Rate:** The business averaged **15.2%** month-over-month revenue growth
- **Q4 Seasonal Peak:** Analysis confirms a significant revenue spike in Q4 (Oct–Dec), typical for e-commerce

### Revenue Chart References
- `visualizations/01_monthly_revenue_trend.png` — Full revenue timeline with 3-month moving average
- `visualizations/07_revenue_growth_rate.png` — MoM growth rate bar chart

---

## 3. Customer Insights

### Customer Segmentation (RFM Analysis)

| Segment | Count | % Share |
|---------|-------|---------|
| Champions              |    359 |    23.9% |
| Potential Loyalists    |    322 |    21.5% |
| Lost Customers         |    286 |    19.1% |
| Loyal Customers        |    284 |    18.9% |
| At Risk                |    248 |    16.5% |


**Key Observations:**
- **Champions** are the highest-value customers: recent, frequent, and high-spending
- **At Risk** and **Lost** customers require targeted win-back campaigns
- **Repeat Purchase Rate of 97.9%** demonstrates strong customer loyalty
- **Retention Rate of 94.2%** is a healthy sign of customer stickiness

### Recommendations
- Launch a **loyalty rewards program** targeting Loyal Customers to elevate them to Champions
- Deploy **re-engagement email campaigns** with personalised offers for At Risk / Lost segments
- Develop **first-purchase incentives** to convert Potential Loyalists

---

## 4. Product Insights

- **Top Revenue Product:** WOOD S/3 CABINET ANT WHITE — generating £81,212.98 in total revenue
- The **top 20 products** account for a disproportionate share of revenue (Pareto principle applies)
- Products with negative quantities (returns) were excluded from revenue calculations

### Recommendations
- **Prioritise inventory investment** in top-20 revenue products
- **Bundle slow-moving products** with bestsellers to clear stock
- Monitor **return rates** per product — high returns may indicate quality or expectation issues

---

## 5. Geographic Insights

- **Top Revenue Country:** United Kingdom — £238,446.68 total revenue
- The UK is the primary market; significant international revenue from Europe and APAC
- Geographic analysis reveals market concentration risk if reliant on a single country

### Recommendations
- **Expand localised marketing** in the 2nd and 3rd largest markets
- Consider **multi-currency pricing** and localised checkout for international customers
- Investigate lower-revenue countries for **growth potential vs. operational cost**

---

## 6. Forecast Insights

| Metric | Value |
|--------|-------|
| **Model** | Linear Regression with Seasonal Features |
| **Train/Test Split** | 80% / 20% |
| **MAE** | £5,206.12 |
| **RMSE** | £6,093.52 |
| **R² Score** | 0.84 |
| **Forecast Period** | 2024-01 – 2024-06 |
| **Projected 6-Month Revenue** | £108,340.13 |

### Forecast Interpretation
- The model captures the underlying **upward revenue trend** and **seasonal patterns**
- An **R² of 0.84** indicates the model explains a meaningful portion of revenue variance
- Forecast should be used as a **directional indicator**, not a precise target

### Charts
- `visualizations/actual_vs_predicted.png` — Model fit vs actuals
- `visualizations/revenue_forecast.png` — 6-month ahead forecast

---

## 7. Strategic Recommendations

### Immediate Actions (0–3 months)
1. **Launch RFM-based email campaigns** — segment-specific messaging for each of the 5 customer groups
2. **Promote top 20 products** — focused advertising spend on highest-revenue SKUs
3. **Reduce cart abandonment** — introduce targeted discounts for customers who haven't purchased in 60 days

### Short-Term (3–6 months)
4. **Implement a subscription or loyalty program** to raise repeat purchase rates
5. **Expand to high-potential international markets** with localised campaigns
6. **Bundle slow-moving stock** with bestsellers for clearance campaigns

### Long-Term (6–12 months)
7. **Build a real-time analytics dashboard** connecting directly to transactional database
8. **Invest in predictive CLV modelling** using advanced ML (XGBoost, LightGBM)
9. **Adopt cohort retention analysis** to track long-term customer value trends
10. **A/B test pricing strategies** for price-sensitive product categories

---

## 8. Data Quality Summary

| Check | Finding |
|-------|---------|
| Missing CustomerIDs | Removed (cannot track behaviour) |
| Missing Descriptions | Filled with 'Unknown Product' |
| Negative Quantities | Removed (returns/cancellations) |
| Invalid Prices (≤ 0) | Removed |
| Cancelled Invoices | Removed (InvoiceNo starting with 'C') |
| Duplicate Rows | Removed |

---

*Report auto-generated by E-Commerce Analytics Platform | Powered by Python & Pandas*
