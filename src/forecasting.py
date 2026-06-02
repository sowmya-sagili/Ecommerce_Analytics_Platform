"""
E-Commerce Customer & Revenue Analytics Platform
=================================================
Module: forecasting.py

Implements monthly revenue forecasting using Linear Regression:
  - Feature engineering on time-series
  - Train/test split (80/20)
  - Evaluation: MAE, MSE, R²
  - Actual vs Predicted chart
  - 6-month future forecast
"""

import os
import json
import logging
import warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")
logger = logging.getLogger(__name__)

BASE_DIR       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_PATH     = os.path.join(BASE_DIR, "data", "processed", "cleaned_data.csv")
FORECAST_PATH  = os.path.join(BASE_DIR, "data", "processed", "forecast_results.csv")
METRICS_PATH   = os.path.join(BASE_DIR, "data", "processed", "forecast_metrics.json")
VIZ_DIR        = os.path.join(BASE_DIR, "visualizations")


def load_monthly_revenue(path: str = CLEAN_PATH) -> pd.DataFrame:
    """Aggregate cleaned data to monthly revenue time-series."""
    df = pd.read_csv(path, parse_dates=["InvoiceDate"])
    monthly = (
        df.groupby("YearMonth")["Revenue"]
          .sum()
          .reset_index()
          .rename(columns={"Revenue": "MonthlyRevenue"})
          .sort_values("YearMonth")
    )
    # Add numeric time index for regression
    monthly["TimeIndex"] = np.arange(len(monthly))
    # Add seasonal features
    monthly["Month"] = pd.to_datetime(monthly["YearMonth"]).dt.month
    monthly["Quarter"] = pd.to_datetime(monthly["YearMonth"]).dt.quarter
    monthly["MonthSin"] = np.sin(2 * np.pi * monthly["Month"] / 12)
    monthly["MonthCos"] = np.cos(2 * np.pi * monthly["Month"] / 12)

    logger.info(f"Monthly revenue series: {len(monthly)} periods")
    return monthly


def build_features(monthly: pd.DataFrame) -> tuple:
    """Build feature matrix X and target vector y."""
    feature_cols = ["TimeIndex", "MonthSin", "MonthCos", "Quarter"]
    X = monthly[feature_cols].values
    y = monthly["MonthlyRevenue"].values
    return X, y, feature_cols


def train_test_split_time(X: np.ndarray, y: np.ndarray,
                           test_size: float = 0.2) -> tuple:
    """Chronological train/test split (no shuffle)."""
    split = int(len(X) * (1 - test_size))
    return X[:split], X[split:], y[:split], y[split:]


def train_model(X_train: np.ndarray, y_train: np.ndarray):
    """Train Linear Regression model."""
    model = LinearRegression()
    model.fit(X_train, y_train)
    logger.info("Linear Regression model trained.")
    return model


def evaluate_model(model, X_test: np.ndarray, y_test: np.ndarray) -> dict:
    """Compute MAE, MSE, RMSE, R² metrics."""
    y_pred = model.predict(X_test)
    metrics = {
        "MAE":  round(mean_absolute_error(y_test, y_pred), 2),
        "MSE":  round(mean_squared_error(y_test, y_pred), 2),
        "RMSE": round(np.sqrt(mean_squared_error(y_test, y_pred)), 2),
        "R2":   round(r2_score(y_test, y_pred), 4),
    }
    logger.info(f"MAE  : £{metrics['MAE']:,.2f}")
    logger.info(f"MSE  : {metrics['MSE']:,.2f}")
    logger.info(f"RMSE : £{metrics['RMSE']:,.2f}")
    logger.info(f"R²   : {metrics['R2']}")
    return metrics


def forecast_future(model, monthly: pd.DataFrame,
                    n_months: int = 6) -> pd.DataFrame:
    """Generate n_months ahead predictions."""
    last_idx   = monthly["TimeIndex"].max()
    last_month = pd.to_datetime(monthly["YearMonth"].iloc[-1])

    future_rows = []
    for i in range(1, n_months + 1):
        future_date = last_month + pd.DateOffset(months=i)
        idx         = last_idx + i
        month       = future_date.month
        quarter     = (month - 1) // 3 + 1
        row = {
            "YearMonth":    future_date.strftime("%Y-%m"),
            "TimeIndex":    idx,
            "Month":        month,
            "Quarter":      quarter,
            "MonthSin":     np.sin(2 * np.pi * month / 12),
            "MonthCos":     np.cos(2 * np.pi * month / 12),
        }
        future_rows.append(row)

    future_df = pd.DataFrame(future_rows)
    feature_cols = ["TimeIndex", "MonthSin", "MonthCos", "Quarter"]
    future_df["ForecastRevenue"] = model.predict(future_df[feature_cols].values)
    future_df["ForecastRevenue"] = future_df["ForecastRevenue"].clip(lower=0).round(2)
    return future_df


def plot_actual_vs_predicted(monthly: pd.DataFrame, model,
                              X_train, X_test, y_train, y_test,
                              split_idx: int,
                              out_dir: str = VIZ_DIR) -> str:
    """Plot actual revenue vs model fitted & predicted values."""
    os.makedirs(out_dir, exist_ok=True)

    train_pred = model.predict(X_train)
    test_pred  = model.predict(X_test)

    months    = monthly["YearMonth"].values
    actuals   = monthly["MonthlyRevenue"].values

    fig, ax = plt.subplots(figsize=(14, 6))
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f8f9fa")

    # Actual line
    ax.plot(months, actuals, color="#6C63FF", linewidth=2.2,
            label="Actual Revenue", zorder=3)
    ax.fill_between(months, actuals, alpha=0.12, color="#6C63FF")

    # Train fit
    ax.plot(months[:split_idx], train_pred, "--", color="#43B6C8",
            linewidth=1.8, label="Train Fit", zorder=4)

    # Test prediction
    ax.plot(months[split_idx:], test_pred, "--", color="#FF6B6B",
            linewidth=2.0, label="Test Prediction", zorder=4)

    # Split marker
    ax.axvline(x=months[split_idx], color="#FFB347", linewidth=1.5,
               linestyle=":", alpha=0.8, label="Train/Test Split")

    ax.set_title("Actual vs Predicted Monthly Revenue", fontsize=14,
                 fontweight="bold", color="#1a1a2e", pad=12)
    ax.set_xlabel("Month", fontsize=11, color="#444")
    ax.set_ylabel("Revenue (£)", fontsize=11, color="#444")
    ax.tick_params(axis="x", rotation=45, colors="#555")
    ax.tick_params(axis="y", colors="#555")
    ax.legend(fontsize=10)

    # Gridlines
    ax.yaxis.grid(True, color="#ddd", linewidth=0.8)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_edgecolor("#ddd")

    plt.tight_layout()
    path = os.path.join(out_dir, "actual_vs_predicted.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved: {path}")
    return path


def plot_forecast(monthly: pd.DataFrame, future_df: pd.DataFrame,
                  out_dir: str = VIZ_DIR) -> str:
    """Plot historical revenue + 6-month future forecast."""
    os.makedirs(out_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(14, 6))
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f8f9fa")

    # Historical
    ax.plot(monthly["YearMonth"], monthly["MonthlyRevenue"],
            color="#6C63FF", linewidth=2.2, label="Historical Revenue", zorder=3)
    ax.fill_between(monthly["YearMonth"], monthly["MonthlyRevenue"],
                    alpha=0.12, color="#6C63FF")

    # Forecast
    ax.plot(future_df["YearMonth"], future_df["ForecastRevenue"],
            "o--", color="#56D79E", linewidth=2.2, markersize=7,
            label="6-Month Forecast", zorder=4)
    ax.fill_between(future_df["YearMonth"], future_df["ForecastRevenue"],
                    alpha=0.18, color="#56D79E")

    # Connector
    last_actual_rev = monthly["MonthlyRevenue"].iloc[-1]
    last_actual_mon = monthly["YearMonth"].iloc[-1]
    first_fc_mon    = future_df["YearMonth"].iloc[0]
    first_fc_rev    = future_df["ForecastRevenue"].iloc[0]
    ax.plot([last_actual_mon, first_fc_mon],
            [last_actual_rev, first_fc_rev],
            "--", color="#aaa", linewidth=1.4, zorder=2)

    ax.axvline(x=last_actual_mon, color="#FFB347", linewidth=1.5,
               linestyle=":", alpha=0.9, label="Forecast Start")

    ax.set_title("Revenue Forecast — Next 6 Months", fontsize=14,
                 fontweight="bold", color="#1a1a2e", pad=12)
    ax.set_xlabel("Month", fontsize=11, color="#444")
    ax.set_ylabel("Revenue (£)", fontsize=11, color="#444")
    ax.tick_params(axis="x", rotation=45, colors="#555")
    ax.tick_params(axis="y", colors="#555")
    ax.legend(fontsize=10)
    ax.yaxis.grid(True, color="#ddd", linewidth=0.8)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_edgecolor("#ddd")

    plt.tight_layout()
    path = os.path.join(out_dir, "revenue_forecast.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved: {path}")
    return path


def run_forecasting(df: pd.DataFrame = None) -> tuple:
    """
    Full forecasting pipeline.

    Returns
    -------
    (metrics: dict, future_df: pd.DataFrame)
    """
    monthly      = load_monthly_revenue(CLEAN_PATH if df is None else None)
    X, y, cols   = build_features(monthly)
    split_idx    = int(len(X) * 0.80)
    X_train, X_test, y_train, y_test = train_test_split_time(X, y)

    model   = train_model(X_train, y_train)
    metrics = evaluate_model(model, X_test, y_test)

    future_df = forecast_future(model, monthly, n_months=6)

    # Save outputs
    os.makedirs(os.path.dirname(FORECAST_PATH), exist_ok=True)
    future_df.to_csv(FORECAST_PATH, index=False)
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)
    logger.info(f"Forecast results saved → {FORECAST_PATH}")
    logger.info(f"Metrics saved → {METRICS_PATH}")

    # Plots
    plot_actual_vs_predicted(monthly, model, X_train, X_test, y_train,
                              y_test, split_idx)
    plot_forecast(monthly, future_df)

    return metrics, future_df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")
    run_forecasting()
