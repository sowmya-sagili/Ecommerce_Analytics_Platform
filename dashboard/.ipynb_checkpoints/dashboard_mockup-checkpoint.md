# Power BI Dashboard Mockup
## E-Commerce Customer & Revenue Analytics Platform

---

## Dashboard Architecture — 4 Pages

---

### Page 1: Executive Overview

**Purpose:** High-level KPI snapshot for senior stakeholders

**Layout (Top Row — KPI Cards):**
```
┌─────────────────┬──────────────────┬────────────────────┬──────────────────┐
│  Total Revenue  │  Total Orders    │  Total Customers   │  Avg Order Value │
│   £XXX,XXX      │    X,XXX         │      X,XXX         │     £XX.XX       │
└─────────────────┴──────────────────┴────────────────────┴──────────────────┘
```

**Layout (Middle — Charts):**
```
┌───────────────────────────────────┬────────────────────────────────────────┐
│  Monthly Revenue Trend (Line)     │  Revenue by Country (Bar / Map)        │
│  X-axis: YearMonth                │  X-axis: Country                       │
│  Y-axis: Revenue                  │  Y-axis: Total Revenue                 │
└───────────────────────────────────┴────────────────────────────────────────┘
```

**Layout (Bottom Row):**
```
┌──────────────────────┬─────────────────────────┬─────────────────────────┐
│  Repeat Purchase %   │  Customer Retention %   │  Revenue Growth MoM %   │
│  (Gauge / KPI)       │  (Gauge / KPI)          │  (Sparkline)            │
└──────────────────────┴─────────────────────────┴─────────────────────────┘
```

**Filters:** Year Slicer | Country Slicer | Date Range Picker

**Power BI Fields:**
- `Period` filtered to `Category = "Revenue"`
- `Value` as aggregated measure

---

### Page 2: Customer Analytics

**Purpose:** Deep-dive into customer segments and behaviour

**Layout:**
```
┌─────────────────────────────────────┬──────────────────────────────────────┐
│  RFM Segment Donut Chart            │  Segment KPI Table                   │
│  Legend: Champions, Loyal, etc.     │  Columns: Segment | Count | Revenue  │
└─────────────────────────────────────┴──────────────────────────────────────┘

┌─────────────────────────────────────┬──────────────────────────────────────┐
│  Customer Purchase Frequency Hist   │  Revenue per Segment (Bar)           │
│  X: # Orders | Y: # Customers       │  X: Segment | Y: £ Revenue           │
└─────────────────────────────────────┴──────────────────────────────────────┘
```

**Filters:** Segment Slicer | Country Slicer

**Key Measures (DAX):**
```dax
Repeat Purchase Rate =
    DIVIDE(
        COUNTROWS(FILTER(customer_summary, customer_summary[TotalOrders] > 1)),
        COUNTROWS(customer_summary)
    ) * 100

Champions Revenue Share =
    DIVIDE(
        CALCULATE(SUM(rfm_segments[Monetary]), rfm_segments[Segment] = "Champions"),
        SUM(rfm_segments[Monetary])
    ) * 100
```

---

### Page 3: Product & Revenue Intelligence

**Purpose:** Identify top-performing and underperforming products

**Layout:**
```
┌──────────────────────────────────────────────────────────────────────────┐
│  Top 20 Products by Revenue (Horizontal Bar Chart)                       │
│  Y-axis: Description | X-axis: Total Revenue | Colour: Revenue band      │
└──────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────┬─────────────────────────────────────────┐
│  Revenue Distribution Hist     │  MoM Revenue Growth Rate (Waterfall)    │
│  X: Order Revenue | Y: Count   │  X: YearMonth | Y: Growth %             │
└────────────────────────────────┴─────────────────────────────────────────┘
```

**Filters:** Product Search Box | Year Slicer | Country

**Key Measures (DAX):**
```dax
Total Revenue =
    SUM(dashboard_dataset[Value])

Top Product Revenue =
    MAXX(
        SUMMARIZE(transactions, transactions[Description],
                  "TotalRev", SUM(transactions[Revenue])),
        [TotalRev]
    )
```

---

### Page 4: Forecast & Future Planning

**Purpose:** Revenue forecast and trend planning

**Layout:**
```
┌──────────────────────────────────────────────────────────────────────────┐
│  Historical + Forecast Revenue (Line Chart with Forecast annotation)     │
│  X-axis: Period | Y-axis: Revenue                                         │
│  Historical (solid) | Forecast (dashed, different colour)                │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┬─────────────────────────┬────────────────────────┐
│  Model MAE           │  Model R² Score         │  6-Month Forecast £    │
│  KPI Card            │  KPI Card               │  KPI Card              │
└──────────────────────┴─────────────────────────┴────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│  Forecast Table: Period | Forecast Revenue | vs Last Year                │
└──────────────────────────────────────────────────────────────────────────┘
```

**Fields:**
- Forecast data from `dashboard_dataset.csv` where `Category = "Forecast"`
- Historical from `Category = "Revenue"` and `Metric = "Monthly Revenue"`

**DAX:**
```dax
Total Forecast Revenue =
    CALCULATE(
        SUM(dashboard_dataset[Value]),
        dashboard_dataset[Category] = "Forecast"
    )
```

---

## Dashboard Dataset Schema

The file `dashboard/dashboard_dataset.csv` has the following structure:

| Column | Type | Description |
|--------|------|-------------|
| `Period` | Text | YearMonth (e.g. "2023-01") or "ALL" for scalars |
| `Metric` | Text | KPI name (e.g. "Monthly Revenue", "Total Orders") |
| `Value` | Float | Numeric metric value |
| `Category` | Text | One of: Revenue, Customer, Product, Geography, Forecast |

## Import Steps in Power BI

1. Open Power BI Desktop
2. **Home → Get Data → Text/CSV**
3. Navigate to `dashboard/dashboard_dataset.csv`
4. Click **Transform Data** to verify columns
5. In **Model View**, ensure `Period` is set as a Date hierarchy
6. Create calculated measures using the DAX examples above
7. Build visuals by dragging `Metric` → filter, `Value` → values axis

---

## Colour Theme

| Element | Hex |
|---------|-----|
| Primary (Revenue) | `#6C63FF` |
| Secondary (Customers) | `#43B6C8` |
| Positive Growth | `#56D79E` |
| Negative / Risk | `#FF6B6B` |
| Forecast | `#FFB347` |
| Background | `#F8F9FA` |
