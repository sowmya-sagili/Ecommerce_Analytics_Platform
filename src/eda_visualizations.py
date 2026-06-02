"""
E-Commerce Customer & Revenue Analytics Platform
=================================================
Module: eda_visualizations.py

Generates all 7 EDA charts and saves them to visualizations/:
  1. Monthly Revenue Trend
  2. Top 20 Products by Revenue
  3. Revenue by Country
  4. Customer Purchase Distribution
  5. Revenue Distribution Histogram
  6. Correlation Heatmap
  7. Revenue Growth Rate (MoM)
"""

import os
import logging
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

logger = logging.getLogger(__name__)

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_PATH = os.path.join(BASE_DIR, "data", "processed", "cleaned_data.csv")
VIZ_DIR    = os.path.join(BASE_DIR, "visualizations")

# ─── Shared style ─────────────────────────────────────────────────────────────
PRIMARY   = "#6C63FF"
SECONDARY = "#43B6C8"
ACCENT    = "#56D79E"
DANGER    = "#FF6B6B"
WARN      = "#FFB347"
BG        = "#f8f9fa"
TEXT      = "#1a1a2e"

def _base_fig(w=12, h=5):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor(BG)
    return fig, ax

def _finalize(fig, path, tight=True):
    if tight:
        plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved: {path}")
    return path

def _grid(ax):
    ax.yaxis.grid(True, color="#ddd", linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_edgecolor("#ddd")


# ─── Chart 1: Monthly Revenue Trend ──────────────────────────────────────────
def plot_monthly_revenue(df: pd.DataFrame, out_dir: str = VIZ_DIR) -> str:
    os.makedirs(out_dir, exist_ok=True)
    monthly = (df.groupby("YearMonth")["Revenue"]
                 .sum().reset_index().sort_values("YearMonth"))

    fig, ax = _base_fig(14, 5)
    ax.plot(monthly["YearMonth"], monthly["Revenue"],
            color=PRIMARY, linewidth=2.4, zorder=3)
    ax.fill_between(monthly["YearMonth"], monthly["Revenue"],
                    alpha=0.15, color=PRIMARY)

    # Moving average
    monthly["MA3"] = monthly["Revenue"].rolling(3, center=True).mean()
    ax.plot(monthly["YearMonth"], monthly["MA3"],
            "--", color=WARN, linewidth=1.8, alpha=0.8, label="3-Month MA")

    ax.set_title("Monthly Revenue Trend", fontsize=14, fontweight="bold",
                 color=TEXT, pad=12)
    ax.set_xlabel("Month", fontsize=11, color="#444")
    ax.set_ylabel("Revenue (£)", fontsize=11, color="#444")
    ax.tick_params(axis="x", rotation=45, colors="#555")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x:,.0f}"))
    ax.legend(fontsize=10)
    _grid(ax)

    path = os.path.join(out_dir, "01_monthly_revenue_trend.png")
    return _finalize(fig, path)


# ─── Chart 2: Top 20 Products by Revenue ─────────────────────────────────────
def plot_top_products(df: pd.DataFrame, out_dir: str = VIZ_DIR) -> str:
    os.makedirs(out_dir, exist_ok=True)
    top = (df.groupby("Description")["Revenue"]
             .sum().reset_index()
             .sort_values("Revenue", ascending=False)
             .head(20))

    fig, ax = _base_fig(12, 8)
    colors = [PRIMARY if i < 5 else SECONDARY for i in range(len(top))]
    bars = ax.barh(top["Description"], top["Revenue"],
                   color=colors, edgecolor="white", height=0.7)

    for bar, val in zip(bars, top["Revenue"]):
        ax.text(bar.get_width() + 10, bar.get_y() + bar.get_height() / 2,
                f"£{val:,.0f}", va="center", ha="left", fontsize=8, color="#333")

    ax.set_title("Top 20 Products by Revenue", fontsize=14, fontweight="bold",
                 color=TEXT, pad=12)
    ax.set_xlabel("Revenue (£)", fontsize=11, color="#444")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x:,.0f}"))
    _grid(ax)
    ax.invert_yaxis()

    path = os.path.join(out_dir, "02_top_20_products.png")
    return _finalize(fig, path)


# ─── Chart 3: Revenue by Country ─────────────────────────────────────────────
def plot_revenue_by_country(df: pd.DataFrame, out_dir: str = VIZ_DIR) -> str:
    os.makedirs(out_dir, exist_ok=True)
    country = (df.groupby("Country")["Revenue"]
                 .sum().reset_index()
                 .sort_values("Revenue", ascending=False)
                 .head(15))

    fig, ax = _base_fig(11, 5)
    palette = [PRIMARY] + [SECONDARY] * (len(country) - 1)
    bars = ax.bar(country["Country"], country["Revenue"],
                  color=palette, edgecolor="white", width=0.65)

    for bar, val in zip(bars, country["Revenue"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 200,
                f"£{val:,.0f}", ha="center", va="bottom", fontsize=8, color="#333",
                rotation=30)

    ax.set_title("Revenue by Country (Top 15)", fontsize=14, fontweight="bold",
                 color=TEXT, pad=12)
    ax.set_xlabel("Country", fontsize=11, color="#444")
    ax.set_ylabel("Revenue (£)", fontsize=11, color="#444")
    ax.tick_params(axis="x", rotation=35, colors="#555")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x:,.0f}"))
    _grid(ax)

    path = os.path.join(out_dir, "03_revenue_by_country.png")
    return _finalize(fig, path)


# ─── Chart 4: Customer Purchase Frequency Distribution ───────────────────────
def plot_purchase_distribution(df: pd.DataFrame, out_dir: str = VIZ_DIR) -> str:
    os.makedirs(out_dir, exist_ok=True)
    order_counts = df.groupby("CustomerID")["InvoiceNo"].nunique()
    capped = order_counts.clip(upper=30)   # cap at 30 for readability

    fig, ax = _base_fig(10, 5)
    ax.hist(capped, bins=30, color=PRIMARY, edgecolor="white", alpha=0.85)
    ax.axvline(capped.mean(), color=DANGER, linewidth=2, linestyle="--",
               label=f"Mean: {capped.mean():.1f}")
    ax.axvline(capped.median(), color=WARN, linewidth=2, linestyle=":",
               label=f"Median: {capped.median():.0f}")

    ax.set_title("Customer Purchase Frequency Distribution", fontsize=14,
                 fontweight="bold", color=TEXT, pad=12)
    ax.set_xlabel("Number of Orders (capped at 30)", fontsize=11, color="#444")
    ax.set_ylabel("Number of Customers", fontsize=11, color="#444")
    ax.legend(fontsize=10)
    _grid(ax)

    path = os.path.join(out_dir, "04_customer_purchase_distribution.png")
    return _finalize(fig, path)


# ─── Chart 5: Revenue Distribution Histogram ─────────────────────────────────
def plot_revenue_distribution(df: pd.DataFrame, out_dir: str = VIZ_DIR) -> str:
    os.makedirs(out_dir, exist_ok=True)
    order_rev = df.groupby("InvoiceNo")["Revenue"].sum()
    capped = order_rev.clip(upper=order_rev.quantile(0.99))

    fig, ax = _base_fig(10, 5)
    ax.hist(capped, bins=50, color=SECONDARY, edgecolor="white", alpha=0.85)
    ax.axvline(capped.mean(), color=DANGER, linewidth=2, linestyle="--",
               label=f"Mean: £{capped.mean():,.2f}")

    ax.set_title("Order Revenue Distribution", fontsize=14, fontweight="bold",
                 color=TEXT, pad=12)
    ax.set_xlabel("Order Revenue (£) — 99th percentile capped", fontsize=11, color="#444")
    ax.set_ylabel("Number of Orders", fontsize=11, color="#444")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x:,.0f}"))
    ax.legend(fontsize=10)
    _grid(ax)

    path = os.path.join(out_dir, "05_revenue_distribution.png")
    return _finalize(fig, path)


# ─── Chart 6: Correlation Heatmap ────────────────────────────────────────────
def plot_correlation_heatmap(df: pd.DataFrame, out_dir: str = VIZ_DIR) -> str:
    os.makedirs(out_dir, exist_ok=True)
    num_cols = ["Quantity", "UnitPrice", "Revenue", "OrderYear",
                "OrderMonth", "OrderDay"]
    corr = df[num_cols].corr()

    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor("#ffffff")
    mask = np.triu(np.ones_like(corr, dtype=bool))   # upper triangle
    sns.heatmap(corr, mask=mask, annot=True, fmt=".2f",
                cmap="coolwarm", center=0,
                linewidths=0.5, linecolor="#fff",
                annot_kws={"size": 11},
                ax=ax, cbar_kws={"shrink": 0.8})

    ax.set_title("Feature Correlation Heatmap", fontsize=14, fontweight="bold",
                 color=TEXT, pad=12)
    ax.tick_params(colors="#444")

    path = os.path.join(out_dir, "06_correlation_heatmap.png")
    return _finalize(fig, path)


# ─── Chart 7: Month-over-Month Revenue Growth Rate ───────────────────────────
def plot_growth_rate(df: pd.DataFrame, out_dir: str = VIZ_DIR) -> str:
    os.makedirs(out_dir, exist_ok=True)
    monthly = (df.groupby("YearMonth")["Revenue"]
                 .sum().reset_index().sort_values("YearMonth"))
    monthly["Growth"] = monthly["Revenue"].pct_change() * 100
    monthly = monthly.dropna(subset=["Growth"])

    fig, ax = _base_fig(14, 5)
    colors = [ACCENT if g >= 0 else DANGER for g in monthly["Growth"]]
    bars = ax.bar(monthly["YearMonth"], monthly["Growth"],
                  color=colors, edgecolor="white", width=0.7)

    ax.axhline(0, color="#555", linewidth=1.2)
    ax.set_title("Month-over-Month Revenue Growth Rate (%)", fontsize=14,
                 fontweight="bold", color=TEXT, pad=12)
    ax.set_xlabel("Month", fontsize=11, color="#444")
    ax.set_ylabel("Growth Rate (%)", fontsize=11, color="#444")
    ax.tick_params(axis="x", rotation=45, colors="#555")
    _grid(ax)

    path = os.path.join(out_dir, "07_revenue_growth_rate.png")
    return _finalize(fig, path)


# ─── Pipeline ─────────────────────────────────────────────────────────────────
def run_eda(df: pd.DataFrame = None) -> list:
    """Generate all 7 EDA charts. Returns list of saved paths."""
    if df is None:
        df = pd.read_csv(CLEAN_PATH, parse_dates=["InvoiceDate"])

    os.makedirs(VIZ_DIR, exist_ok=True)
    paths = [
        plot_monthly_revenue(df),
        plot_top_products(df),
        plot_revenue_by_country(df),
        plot_purchase_distribution(df),
        plot_revenue_distribution(df),
        plot_correlation_heatmap(df),
        plot_growth_rate(df),
    ]
    logger.info(f"Generated {len(paths)} EDA charts.")
    return paths


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")
    run_eda()
