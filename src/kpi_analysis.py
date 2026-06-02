"""
E-Commerce Customer & Revenue Analytics Platform
=================================================
Module: kpi_analysis.py

Calculates and returns all key KPI metrics:
  - Total Revenue, Orders, Customers
  - Average Order Value
  - Revenue per Customer
  - Monthly Growth Rate
  - Customer Retention Rate
  - Repeat Purchase Rate
"""

import os
import json
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_PATH   = os.path.join(BASE_DIR, "data", "processed", "cleaned_data.csv")
KPI_OUT_JSON = os.path.join(BASE_DIR, "data", "processed", "kpis.json")
KPI_OUT_CSV  = os.path.join(BASE_DIR, "data", "processed", "kpis.csv")


def load_cleaned_data(path: str = CLEAN_PATH) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["InvoiceDate"])
    logger.info(f"Loaded cleaned data: {df.shape}")
    return df


def calc_total_revenue(df: pd.DataFrame) -> float:
    return round(df["Revenue"].sum(), 2)


def calc_total_orders(df: pd.DataFrame) -> int:
    return df["InvoiceNo"].nunique()


def calc_total_customers(df: pd.DataFrame) -> int:
    return df["CustomerID"].nunique()


def calc_avg_order_value(df: pd.DataFrame) -> float:
    order_totals = df.groupby("InvoiceNo")["Revenue"].sum()
    return round(order_totals.mean(), 2)


def calc_revenue_per_customer(df: pd.DataFrame) -> float:
    rev   = calc_total_revenue(df)
    custs = calc_total_customers(df)
    return round(rev / custs, 2) if custs > 0 else 0.0


def calc_monthly_growth_rate(df: pd.DataFrame) -> dict:
    """
    Returns a dict mapping YearMonth → revenue,
    plus the average month-over-month growth rate (%).
    """
    monthly = (
        df.groupby("YearMonth")["Revenue"]
          .sum()
          .reset_index()
          .sort_values("YearMonth")
    )
    monthly["GrowthRate"] = monthly["Revenue"].pct_change() * 100
    avg_growth = round(monthly["GrowthRate"].mean(), 2)
    monthly_dict = monthly.set_index("YearMonth")["Revenue"].to_dict()
    return {"monthly_revenue": monthly_dict, "avg_monthly_growth_pct": avg_growth}


def calc_repeat_purchase_rate(df: pd.DataFrame) -> float:
    """Percentage of customers who made more than 1 order."""
    order_counts = df.groupby("CustomerID")["InvoiceNo"].nunique()
    repeat = (order_counts > 1).sum()
    total  = len(order_counts)
    return round((repeat / total) * 100, 2) if total > 0 else 0.0


def calc_retention_rate(df: pd.DataFrame) -> float:
    """
    Simple cohort retention: fraction of customers who purchased
    in both first half and second half of the date range.
    """
    df = df.copy()
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    mid = df["InvoiceDate"].min() + (df["InvoiceDate"].max() - df["InvoiceDate"].min()) / 2

    cohort1 = set(df[df["InvoiceDate"] <= mid]["CustomerID"].unique())
    cohort2 = set(df[df["InvoiceDate"] >  mid]["CustomerID"].unique())

    retained = len(cohort1 & cohort2)
    rate     = round((retained / len(cohort1)) * 100, 2) if cohort1 else 0.0
    return rate


def calc_top_products(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return (
        df.groupby(["StockCode", "Description"])["Revenue"]
          .sum()
          .reset_index()
          .sort_values("Revenue", ascending=False)
          .head(n)
    )


def calc_top_countries(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return (
        df.groupby("Country")["Revenue"]
          .sum()
          .reset_index()
          .sort_values("Revenue", ascending=False)
          .head(n)
    )


def compute_all_kpis(df: pd.DataFrame) -> dict:
    """Compute and return all KPIs as a dictionary."""
    logger.info("Computing KPIs...")

    monthly_data = calc_monthly_growth_rate(df)

    kpis = {
        "total_revenue":          calc_total_revenue(df),
        "total_orders":           calc_total_orders(df),
        "total_customers":        calc_total_customers(df),
        "avg_order_value":        calc_avg_order_value(df),
        "revenue_per_customer":   calc_revenue_per_customer(df),
        "repeat_purchase_rate":   calc_repeat_purchase_rate(df),
        "customer_retention_rate": calc_retention_rate(df),
        "avg_monthly_growth_pct": monthly_data["avg_monthly_growth_pct"],
        "monthly_revenue":        monthly_data["monthly_revenue"],
    }

    logger.info(f"Total Revenue         : £{kpis['total_revenue']:,.2f}")
    logger.info(f"Total Orders          : {kpis['total_orders']:,}")
    logger.info(f"Total Customers       : {kpis['total_customers']:,}")
    logger.info(f"Avg Order Value       : £{kpis['avg_order_value']:,.2f}")
    logger.info(f"Revenue per Customer  : £{kpis['revenue_per_customer']:,.2f}")
    logger.info(f"Repeat Purchase Rate  : {kpis['repeat_purchase_rate']}%")
    logger.info(f"Customer Retention    : {kpis['customer_retention_rate']}%")
    logger.info(f"Avg Monthly Growth    : {kpis['avg_monthly_growth_pct']}%")

    return kpis


def save_kpis(kpis: dict,
              json_path: str = KPI_OUT_JSON,
              csv_path:  str = KPI_OUT_CSV) -> None:
    """Persist KPIs to JSON and flat CSV."""
    os.makedirs(os.path.dirname(json_path), exist_ok=True)

    # JSON — includes nested monthly revenue
    with open(json_path, "w") as f:
        json.dump(kpis, f, indent=2)
    logger.info(f"KPIs saved → {json_path}")

    # Flat CSV (scalar KPIs only)
    scalar_kpis = {k: v for k, v in kpis.items() if not isinstance(v, dict)}
    pd.DataFrame([scalar_kpis]).to_csv(csv_path, index=False)
    logger.info(f"KPIs saved → {csv_path}")


def run_kpi_analysis(df: pd.DataFrame = None) -> dict:
    """Full KPI analysis pipeline."""
    if df is None:
        df = load_cleaned_data()
    kpis = compute_all_kpis(df)
    save_kpis(kpis)
    return kpis


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")
    kpis = run_kpi_analysis()
