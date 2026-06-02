"""
E-Commerce Customer & Revenue Analytics Platform
=================================================
Module: data_cleaning.py

Handles:
  - Loading raw CSV
  - Missing value treatment
  - Duplicate removal
  - Invalid price / negative quantity removal
  - Feature engineering (Revenue, date parts, CLV)
  - Saving cleaned dataset to data/processed/
"""

import os
import logging
import pandas as pd
import numpy as np

# ─── Logging Setup ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH      = os.path.join(BASE_DIR, "data", "raw",       "ecommerce_data.csv")
CLEAN_PATH    = os.path.join(BASE_DIR, "data", "processed", "cleaned_data.csv")
CUSTOMER_PATH = os.path.join(BASE_DIR, "data", "processed", "customer_summary.csv")


# ─── Core Functions ───────────────────────────────────────────────────────────

def load_raw_data(path: str = RAW_PATH) -> pd.DataFrame:
    """Load raw CSV and parse InvoiceDate."""
    logger.info(f"Loading raw data from: {path}")
    df = pd.read_csv(path, parse_dates=["InvoiceDate"], dtype={"CustomerID": str})
    logger.info(f"Raw shape: {df.shape}")
    return df


def report_quality(df: pd.DataFrame, label: str = "Dataset") -> None:
    """Log data quality summary."""
    logger.info(f"--- {label} Quality Report ---")
    logger.info(f"  Shape          : {df.shape}")
    logger.info(f"  Null values    : {df.isnull().sum().sum()}")
    logger.info(f"  Duplicates     : {df.duplicated().sum()}")
    logger.info(f"  Neg quantities : {(df['Quantity'] < 0).sum()}")
    logger.info(f"  Invalid prices : {(df['UnitPrice'] <= 0).sum()}")


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Drop fully-duplicated rows."""
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)
    logger.info(f"Removed {removed} duplicate rows.")
    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Strategy:
      - CustomerID null  → drop row (can't track customer behaviour)
      - Description null → fill with 'Unknown Product'
    """
    before = len(df)

    # Fill missing descriptions
    null_desc = df["Description"].isnull().sum()
    df["Description"] = df["Description"].fillna("Unknown Product")
    logger.info(f"Filled {null_desc} missing Descriptions with 'Unknown Product'.")

    # Drop rows with no CustomerID
    df = df.dropna(subset=["CustomerID"])
    removed = before - len(df)
    logger.info(f"Removed {removed} rows with missing CustomerID.")

    return df


def remove_invalid_prices(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows where UnitPrice <= 0 (free, test, or error records)."""
    before = len(df)
    df = df[df["UnitPrice"] > 0]
    logger.info(f"Removed {before - len(df)} rows with invalid UnitPrice (≤ 0).")
    return df


def remove_negative_quantities(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows with negative Quantity (returns/cancellations)."""
    before = len(df)
    df = df[df["Quantity"] > 0]
    logger.info(f"Removed {before - len(df)} rows with negative/zero Quantity.")
    return df


def remove_cancelled_invoices(df: pd.DataFrame) -> pd.DataFrame:
    """Remove cancelled invoices (InvoiceNo starts with 'C')."""
    before = len(df)
    df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]
    logger.info(f"Removed {before - len(df)} cancelled invoice rows.")
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Feature engineering:
      - Revenue = Quantity × UnitPrice
      - OrderMonth, OrderYear, OrderDay, OrderDayOfWeek
      - YearMonth string for grouping
    """
    logger.info("Engineering features...")

    # Core revenue metric
    df["Revenue"] = (df["Quantity"] * df["UnitPrice"]).round(2)

    # Date-based features
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["OrderYear"]      = df["InvoiceDate"].dt.year
    df["OrderMonth"]     = df["InvoiceDate"].dt.month
    df["OrderDay"]       = df["InvoiceDate"].dt.day
    df["OrderDayOfWeek"] = df["InvoiceDate"].dt.day_name()
    df["YearMonth"]      = df["InvoiceDate"].dt.to_period("M").astype(str)

    logger.info("Features created: Revenue, OrderYear, OrderMonth, OrderDay, OrderDayOfWeek, YearMonth")
    return df


def build_customer_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate per-customer stats:
      - TotalRevenue (Customer Lifetime Revenue)
      - TotalOrders
      - TotalItems
      - AvgOrderValue
      - FirstPurchase / LastPurchase / TenureDays
    """
    logger.info("Building customer-level summary...")

    summary = df.groupby("CustomerID").agg(
        TotalRevenue   = ("Revenue",    "sum"),
        TotalOrders    = ("InvoiceNo",  "nunique"),
        TotalItems     = ("Quantity",   "sum"),
        FirstPurchase  = ("InvoiceDate","min"),
        LastPurchase   = ("InvoiceDate","max"),
        Country        = ("Country",    lambda x: x.mode()[0]),
    ).reset_index()

    summary["AvgOrderValue"] = (summary["TotalRevenue"] / summary["TotalOrders"]).round(2)
    summary["TenureDays"]    = (summary["LastPurchase"] - summary["FirstPurchase"]).dt.days

    logger.info(f"Customer summary shape: {summary.shape}")
    return summary


def run_cleaning_pipeline(raw_path: str = RAW_PATH,
                          clean_path: str = CLEAN_PATH,
                          customer_path: str = CUSTOMER_PATH) -> pd.DataFrame:
    """
    Full data cleaning pipeline.

    Returns
    -------
    pd.DataFrame  Cleaned transaction-level dataframe.
    """
    os.makedirs(os.path.dirname(clean_path), exist_ok=True)

    df = load_raw_data(raw_path)
    report_quality(df, "RAW")

    df = remove_duplicates(df)
    df = handle_missing_values(df)
    df = remove_invalid_prices(df)
    df = remove_negative_quantities(df)
    df = remove_cancelled_invoices(df)
    df = engineer_features(df)

    report_quality(df, "CLEANED")

    # Save cleaned transactions
    df.to_csv(clean_path, index=False)
    logger.info(f"Cleaned dataset saved → {clean_path}")

    # Save customer summary
    customer_df = build_customer_summary(df)
    customer_df.to_csv(customer_path, index=False)
    logger.info(f"Customer summary saved → {customer_path}")

    return df


# ─── Entry Point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    run_cleaning_pipeline()
