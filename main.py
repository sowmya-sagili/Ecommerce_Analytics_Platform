"""
E-Commerce Customer & Revenue Analytics Platform
=================================================
main.py — Full Pipeline Orchestrator

Run this single script to execute the complete analytics pipeline:
  1. Generate synthetic dataset
  2. Clean & preprocess data
  3. Compute KPIs
  4. Run EDA (7 charts)
  5. Customer Segmentation (RFM)
  6. Forecasting (Linear Regression)
  7. Dashboard dataset export
  8. Business report generation

Usage:
    python main.py

Output:
    data/processed/   — cleaned CSV, customer summary, KPIs, forecast
    visualizations/   — 11 PNG charts
    dashboard/        — Power BI-ready CSV
    reports/          — business_report.md
"""

import os
import sys
import time
import logging
from datetime import datetime

# ─── Logging Setup ────────────────────────────────────────────────────────────
import io
_stdout_handler = logging.StreamHandler(io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace'))
_file_handler   = logging.FileHandler(
    os.path.join(os.path.dirname(__file__), "reports", "pipeline.log"),
    mode="w", encoding="utf-8",
)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[_stdout_handler, _file_handler],
)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR  = os.path.join(BASE_DIR, "src")
sys.path.insert(0, SRC_DIR)
os.environ.setdefault("PYTHONIOENCODING", "utf-8")


# ─── Pipeline Steps ───────────────────────────────────────────────────────────

def step(name: str):
    """Decorator-style context printer."""
    def decorator(fn):
        def wrapper(*args, **kwargs):
            banner = "-" * 60
            logger.info(banner)
            logger.info(f"  STEP: {name}")
            logger.info(banner)
            t0 = time.time()
            result = fn(*args, **kwargs)
            elapsed = time.time() - t0
            logger.info(f"  Done in {elapsed:.1f}s")
            return result
        return wrapper
    return decorator


@step("Generate Synthetic Dataset")
def run_data_generation():
    from generate_data import generate_dataset
    import pandas as pd
    raw_path = os.path.join(BASE_DIR, "data", "raw", "ecommerce_data.csv")
    if os.path.exists(raw_path):
        logger.info(f"Raw dataset already exists ({raw_path}). Skipping generation.")
        return pd.read_csv(raw_path)
    os.makedirs(os.path.dirname(raw_path), exist_ok=True)
    df = generate_dataset(10000)
    df.to_csv(raw_path, index=False)
    logger.info(f"Dataset generated: {df.shape[0]:,} rows, {df.shape[1]} columns")
    return df


@step("Data Cleaning & Feature Engineering")
def run_cleaning():
    from data_cleaning import run_cleaning_pipeline
    return run_cleaning_pipeline()


@step("KPI Analysis")
def run_kpis(df):
    from kpi_analysis import run_kpi_analysis
    return run_kpi_analysis(df)


@step("Exploratory Data Analysis (7 Charts)")
def run_eda(df):
    from eda_visualizations import run_eda
    paths = run_eda(df)
    logger.info(f"Generated {len(paths)} EDA charts.")
    return paths


@step("Customer Segmentation (RFM)")
def run_segmentation(df):
    from customer_segmentation import run_segmentation
    rfm = run_segmentation(df)
    logger.info(f"Segmented {len(rfm):,} customers into 5 RFM groups.")
    return rfm


@step("Revenue Forecasting")
def run_forecast():
    from forecasting import run_forecasting
    metrics, future_df = run_forecasting()
    logger.info(f"Forecast metrics: MAE={metrics['MAE']}, R²={metrics['R2']}")
    return metrics, future_df


@step("Dashboard Dataset Export")
def run_dashboard():
    from dashboard_data_generator import run_dashboard_generator
    path = run_dashboard_generator()
    logger.info(f"Dashboard dataset exported → {path}")
    return path


@step("Business Insights Report")
def run_report():
    from report_generator import run_report_generator
    path = run_report_generator()
    logger.info(f"Report generated → {path}")
    return path


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(os.path.join(BASE_DIR, "reports"), exist_ok=True)

    start_time = time.time()
    logger.info("=" * 60)
    logger.info("  E-COMMERCE ANALYTICS PLATFORM — PIPELINE START")
    logger.info(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    try:
        # 1. Generate data
        run_data_generation()

        # 2. Clean data
        df = run_cleaning()

        # 3. KPIs
        kpis = run_kpis(df)

        # 4. EDA
        run_eda(df)

        # 5. Segmentation
        rfm = run_segmentation(df)

        # 6. Forecast
        metrics, future_df = run_forecast()

        # 7. Dashboard
        run_dashboard()

        # 8. Report
        run_report()

        total = time.time() - start_time
        logger.info("=" * 60)
        logger.info(f"  PIPELINE COMPLETE in {total:.1f}s")
        logger.info("")
        logger.info("  Key Results:")
        logger.info(f"    Total Revenue     : {kpis.get('total_revenue', 0):>14,.2f}")
        logger.info(f"    Total Orders      : {kpis.get('total_orders', 0):>14,}")
        logger.info(f"    Total Customers   : {kpis.get('total_customers', 0):>14,}")
        logger.info(f"    Avg Order Value   : {kpis.get('avg_order_value', 0):>14,.2f}")
        logger.info(f"    Repeat Purchase % : {kpis.get('repeat_purchase_rate', 0):>13.1f}%")
        logger.info(f"    Forecast R2       : {metrics.get('R2', 0):>14.4f}")
        logger.info("")
        logger.info("  Output Files:")
        logger.info("    data/processed/cleaned_data.csv")
        logger.info("    data/processed/rfm_segments.csv")
        logger.info("    data/processed/forecast_results.csv")
        logger.info("    data/processed/ecommerce.db")
        logger.info("    visualizations/  (11 PNG charts)")
        logger.info("    dashboard/dashboard_dataset.csv")
        logger.info("    reports/business_report.md")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
