"""
E-Commerce Customer & Revenue Analytics Platform
=================================================
Module: dashboard_data_generator.py

Builds Power BI-ready dashboard dataset by aggregating:
  - Revenue KPIs
  - Customer KPIs (incl. RFM segments)
  - Product KPIs
  - Country KPIs
  - Forecast KPIs
  - Monthly time-series

Also creates the SQLite database for SQL analytics.
"""

import os
import json
import logging
import sqlite3
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_PATH    = os.path.join(BASE_DIR, "data", "processed", "cleaned_data.csv")
CUSTOMER_PATH = os.path.join(BASE_DIR, "data", "processed", "customer_summary.csv")
RFM_PATH      = os.path.join(BASE_DIR, "data", "processed", "rfm_segments.csv")
FORECAST_PATH = os.path.join(BASE_DIR, "data", "processed", "forecast_results.csv")
KPI_PATH      = os.path.join(BASE_DIR, "data", "processed", "kpis.json")
DASH_PATH     = os.path.join(BASE_DIR, "dashboard", "dashboard_dataset.csv")
DB_PATH       = os.path.join(BASE_DIR, "data", "processed", "ecommerce.db")


# ─── Load helpers ─────────────────────────────────────────────────────────────

def _load(path, **kwargs):
    if os.path.exists(path):
        return pd.read_csv(path, **kwargs)
    logger.warning(f"File not found: {path}")
    return pd.DataFrame()


# ─── Dashboard Sections ───────────────────────────────────────────────────────

def build_revenue_kpis(df: pd.DataFrame, kpis: dict) -> pd.DataFrame:
    monthly = (df.groupby("YearMonth")["Revenue"]
                 .sum().reset_index()
                 .sort_values("YearMonth"))
    monthly["GrowthRate"] = monthly["Revenue"].pct_change() * 100
    monthly["Category"]   = "Revenue"
    monthly = monthly.rename(columns={"Revenue": "Value",
                                      "YearMonth": "Period"})
    monthly["Metric"] = "Monthly Revenue"

    scalar_rows = [
        {"Period": "ALL", "Metric": "Total Revenue",
         "Value": kpis.get("total_revenue", 0), "Category": "Revenue"},
        {"Period": "ALL", "Metric": "Avg Monthly Growth %",
         "Value": kpis.get("avg_monthly_growth_pct", 0), "Category": "Revenue"},
    ]
    return pd.concat([monthly[["Period","Metric","Value","Category"]],
                      pd.DataFrame(scalar_rows)], ignore_index=True)


def build_customer_kpis(kpis: dict, rfm: pd.DataFrame) -> pd.DataFrame:
    rows = [
        {"Period": "ALL", "Metric": "Total Customers",
         "Value": kpis.get("total_customers", 0), "Category": "Customer"},
        {"Period": "ALL", "Metric": "Total Orders",
         "Value": kpis.get("total_orders", 0), "Category": "Customer"},
        {"Period": "ALL", "Metric": "Avg Order Value",
         "Value": kpis.get("avg_order_value", 0), "Category": "Customer"},
        {"Period": "ALL", "Metric": "Revenue per Customer",
         "Value": kpis.get("revenue_per_customer", 0), "Category": "Customer"},
        {"Period": "ALL", "Metric": "Repeat Purchase Rate %",
         "Value": kpis.get("repeat_purchase_rate", 0), "Category": "Customer"},
        {"Period": "ALL", "Metric": "Customer Retention Rate %",
         "Value": kpis.get("customer_retention_rate", 0), "Category": "Customer"},
    ]

    if not rfm.empty:
        seg_counts = rfm["Segment"].value_counts().reset_index()
        seg_counts.columns = ["Metric", "Value"]
        seg_counts["Metric"]   = "Segment: " + seg_counts["Metric"]
        seg_counts["Period"]   = "ALL"
        seg_counts["Category"] = "Customer"
        rows_df = pd.DataFrame(rows)
        return pd.concat([rows_df, seg_counts[["Period","Metric","Value","Category"]]],
                         ignore_index=True)
    return pd.DataFrame(rows)


def build_product_kpis(df: pd.DataFrame) -> pd.DataFrame:
    top_prod = (df.groupby("Description")["Revenue"]
                  .sum().reset_index()
                  .sort_values("Revenue", ascending=False)
                  .head(20))
    top_prod["Metric"]   = "Product Revenue: " + top_prod["Description"]
    top_prod["Period"]   = "ALL"
    top_prod["Category"] = "Product"
    return top_prod.rename(columns={"Revenue": "Value"})[["Period","Metric","Value","Category"]]


def build_country_kpis(df: pd.DataFrame) -> pd.DataFrame:
    country = (df.groupby("Country")["Revenue"]
                 .sum().reset_index()
                 .sort_values("Revenue", ascending=False))
    country["Metric"]   = "Country Revenue: " + country["Country"]
    country["Period"]   = "ALL"
    country["Category"] = "Geography"
    return country.rename(columns={"Revenue": "Value"})[["Period","Metric","Value","Category"]]


def build_forecast_kpis(forecast: pd.DataFrame) -> pd.DataFrame:
    if forecast.empty:
        return pd.DataFrame()
    fc = forecast.rename(columns={"YearMonth": "Period",
                                   "ForecastRevenue": "Value"})
    fc["Metric"]   = "Forecast Revenue"
    fc["Category"] = "Forecast"
    return fc[["Period","Metric","Value","Category"]]


# ─── SQLite Database ──────────────────────────────────────────────────────────

def build_sqlite_db(df: pd.DataFrame, rfm: pd.DataFrame,
                    customer: pd.DataFrame) -> str:
    """
    Create an SQLite database with three tables:
      - transactions
      - rfm_segments
      - customer_summary
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Remove existing DB for clean slate
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    try:
        df.to_sql("transactions",    conn, if_exists="replace", index=False)
        logger.info("SQLite: transactions table loaded.")

        if not rfm.empty:
            rfm.to_sql("rfm_segments", conn, if_exists="replace", index=False)
            logger.info("SQLite: rfm_segments table loaded.")

        if not customer.empty:
            customer.to_sql("customer_summary", conn, if_exists="replace", index=False)
            logger.info("SQLite: customer_summary table loaded.")

        # Create useful indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_cust ON transactions(CustomerID)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_date ON transactions(InvoiceDate)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_stock ON transactions(StockCode)")
        conn.commit()
        logger.info(f"SQLite database created → {DB_PATH}")
    finally:
        conn.close()

    return DB_PATH


# ─── Pipeline ─────────────────────────────────────────────────────────────────

def run_dashboard_generator() -> str:
    """Full dashboard dataset generation pipeline."""
    os.makedirs(os.path.dirname(DASH_PATH), exist_ok=True)

    df       = _load(CLEAN_PATH,    parse_dates=["InvoiceDate"])
    customer = _load(CUSTOMER_PATH)
    rfm      = _load(RFM_PATH)
    forecast = _load(FORECAST_PATH)

    kpis = {}
    if os.path.exists(KPI_PATH):
        with open(KPI_PATH) as f:
            kpis = json.load(f)

    # Build each section
    sections = [
        build_revenue_kpis(df, kpis),
        build_customer_kpis(kpis, rfm),
        build_product_kpis(df),
        build_country_kpis(df),
        build_forecast_kpis(forecast),
    ]
    dashboard_df = pd.concat([s for s in sections if not s.empty], ignore_index=True)
    dashboard_df["Value"] = dashboard_df["Value"].round(2)

    dashboard_df.to_csv(DASH_PATH, index=False)
    logger.info(f"Dashboard dataset saved ({len(dashboard_df)} rows) → {DASH_PATH}")

    # Build SQLite DB
    build_sqlite_db(df, rfm, customer)

    return DASH_PATH


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")
    run_dashboard_generator()
