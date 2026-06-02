"""
E-Commerce Customer & Revenue Analytics Platform
=================================================
Module: customer_segmentation.py

Implements RFM Analysis:
  - Recency   : Days since last purchase
  - Frequency : Number of unique orders
  - Monetary  : Total spend

Segments customers into:
  Champions, Loyal Customers, Potential Loyalists,
  At Risk, Lost Customers

Generates visualizations and exports segmentation CSV.
"""

import os
import logging
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

logger = logging.getLogger(__name__)

BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_PATH    = os.path.join(BASE_DIR, "data", "processed", "cleaned_data.csv")
SEG_OUT_PATH  = os.path.join(BASE_DIR, "data", "processed", "rfm_segments.csv")
VIZ_DIR       = os.path.join(BASE_DIR, "visualizations")

# ─── Colour palette ───────────────────────────────────────────────────────────
SEGMENT_COLORS = {
    "Champions":          "#6C63FF",
    "Loyal Customers":    "#43B6C8",
    "Potential Loyalists":"#56D79E",
    "At Risk":            "#FFB347",
    "Lost Customers":     "#FF6B6B",
}


def load_data(path: str = CLEAN_PATH) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["InvoiceDate"])
    logger.info(f"Loaded cleaned data: {df.shape}")
    return df


# ─── RFM Calculation ──────────────────────────────────────────────────────────

def compute_rfm(df: pd.DataFrame, snapshot_date: pd.Timestamp = None) -> pd.DataFrame:
    """
    Compute RFM metrics per customer.

    Parameters
    ----------
    df            : Cleaned transaction DataFrame
    snapshot_date : Reference date for Recency; defaults to max date + 1 day
    """
    if snapshot_date is None:
        snapshot_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)

    logger.info(f"RFM snapshot date: {snapshot_date.date()}")

    rfm = df.groupby("CustomerID").agg(
        Recency   = ("InvoiceDate", lambda x: (snapshot_date - x.max()).days),
        Frequency = ("InvoiceNo",   "nunique"),
        Monetary  = ("Revenue",     "sum"),
    ).reset_index()

    rfm["Monetary"] = rfm["Monetary"].round(2)
    logger.info(f"RFM table shape: {rfm.shape}")
    return rfm


def score_rfm(rfm: pd.DataFrame, q: int = 4) -> pd.DataFrame:
    """
    Assign quantile-based scores (1–q) for each RFM dimension.
    Recency is reverse-scored (lower recency → higher score).
    """
    rfm = rfm.copy()

    # Use rank to handle ties; percentage-based quantile
    rfm["R_Score"] = pd.qcut(rfm["Recency"].rank(method="first"),
                              q=q, labels=range(q, 0, -1)).astype(int)
    rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"),
                              q=q, labels=range(1, q + 1)).astype(int)
    rfm["M_Score"] = pd.qcut(rfm["Monetary"].rank(method="first"),
                              q=q, labels=range(1, q + 1)).astype(int)

    rfm["RFM_Score"] = rfm["R_Score"] + rfm["F_Score"] + rfm["M_Score"]
    rfm["RFM_Segment_Code"] = (rfm["R_Score"].astype(str) +
                                rfm["F_Score"].astype(str) +
                                rfm["M_Score"].astype(str))
    return rfm


def assign_segment(rfm: pd.DataFrame) -> pd.DataFrame:
    """Map RFM scores to human-readable customer segments."""
    def _label(row):
        r, f, m = row["R_Score"], row["F_Score"], row["M_Score"]
        score   = row["RFM_Score"]

        if r >= 3 and f >= 3 and m >= 3:
            return "Champions"
        elif r >= 3 and f >= 2:
            return "Loyal Customers"
        elif r >= 2 and f >= 1 and m >= 2:
            return "Potential Loyalists"
        elif r <= 2 and f >= 2:
            return "At Risk"
        else:
            return "Lost Customers"

    rfm["Segment"] = rfm.apply(_label, axis=1)
    counts = rfm["Segment"].value_counts()
    for seg, cnt in counts.items():
        logger.info(f"  {seg:<22}: {cnt:>5} customers ({cnt/len(rfm)*100:.1f}%)")
    return rfm


# ─── Visualisations ───────────────────────────────────────────────────────────

def _style_ax(ax, title: str, xlabel: str = "", ylabel: str = "") -> None:
    ax.set_title(title, fontsize=14, fontweight="bold", pad=12, color="#1a1a2e")
    ax.set_xlabel(xlabel, fontsize=11, color="#444")
    ax.set_ylabel(ylabel, fontsize=11, color="#444")
    ax.tick_params(colors="#555")
    for spine in ax.spines.values():
        spine.set_edgecolor("#ddd")
    ax.set_facecolor("#f8f9fa")


def plot_segment_distribution(rfm: pd.DataFrame, out_dir: str = VIZ_DIR) -> str:
    """Horizontal bar chart — customer count per segment."""
    os.makedirs(out_dir, exist_ok=True)
    counts = rfm["Segment"].value_counts().sort_values()

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor("#ffffff")
    bars = ax.barh(counts.index, counts.values,
                   color=[SEGMENT_COLORS.get(s, "#aaa") for s in counts.index],
                   edgecolor="white", height=0.6)

    for bar, val in zip(bars, counts.values):
        ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height() / 2,
                f"{val:,}", va="center", ha="left", fontsize=10, color="#333")

    _style_ax(ax, "Customer Segment Distribution (RFM)",
              "Number of Customers", "Segment")
    plt.tight_layout()

    path = os.path.join(out_dir, "rfm_segment_distribution.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved: {path}")
    return path


def plot_rfm_scatter(rfm: pd.DataFrame, out_dir: str = VIZ_DIR) -> str:
    """Scatter — Frequency vs Monetary coloured by Segment."""
    os.makedirs(out_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(11, 6))
    fig.patch.set_facecolor("#ffffff")

    for seg, grp in rfm.groupby("Segment"):
        ax.scatter(grp["Frequency"], grp["Monetary"],
                   label=seg, alpha=0.65, s=40,
                   color=SEGMENT_COLORS.get(seg, "#aaa"),
                   edgecolors="none")

    _style_ax(ax, "RFM: Frequency vs Monetary Value by Segment",
              "Order Frequency", "Monetary Value (£)")
    ax.legend(title="Segment", bbox_to_anchor=(1.01, 1), borderaxespad=0)
    plt.tight_layout()

    path = os.path.join(out_dir, "rfm_scatter.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved: {path}")
    return path


def plot_rfm_boxplots(rfm: pd.DataFrame, out_dir: str = VIZ_DIR) -> str:
    """Box plots of Recency, Frequency, Monetary per segment."""
    os.makedirs(out_dir, exist_ok=True)

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.patch.set_facecolor("#ffffff")
    metrics = ["Recency", "Frequency", "Monetary"]

    for ax, metric in zip(axes, metrics):
        order = rfm.groupby("Segment")[metric].median().sort_values(
            ascending=(metric != "Recency")).index.tolist()
        palette = [SEGMENT_COLORS.get(s, "#aaa") for s in order]
        sns.boxplot(data=rfm, x="Segment", y=metric, order=order,
                    palette=palette, ax=ax, linewidth=0.8)
        _style_ax(ax, f"{metric} by Segment", "Segment", metric)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=25, ha="right", fontsize=9)

    fig.suptitle("RFM Metrics Distribution by Segment",
                 fontsize=15, fontweight="bold", color="#1a1a2e", y=1.02)
    plt.tight_layout()

    path = os.path.join(out_dir, "rfm_boxplots.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved: {path}")
    return path


def plot_segment_revenue(rfm: pd.DataFrame, out_dir: str = VIZ_DIR) -> str:
    """Total monetary value contributed by each segment."""
    os.makedirs(out_dir, exist_ok=True)

    seg_rev = (rfm.groupby("Segment")["Monetary"]
                  .sum()
                  .sort_values(ascending=False)
                  .reset_index())

    fig, ax = plt.subplots(figsize=(9, 5))
    fig.patch.set_facecolor("#ffffff")
    bars = ax.bar(seg_rev["Segment"], seg_rev["Monetary"],
                  color=[SEGMENT_COLORS.get(s, "#aaa") for s in seg_rev["Segment"]],
                  edgecolor="white", width=0.55)

    for bar, val in zip(bars, seg_rev["Monetary"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 200,
                f"£{val:,.0f}", ha="center", va="bottom", fontsize=9, color="#333")

    _style_ax(ax, "Total Revenue Contribution by Customer Segment",
              "Segment", "Revenue (£)")
    plt.tight_layout()

    path = os.path.join(out_dir, "rfm_segment_revenue.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved: {path}")
    return path


# ─── Pipeline ─────────────────────────────────────────────────────────────────

def run_segmentation(df: pd.DataFrame = None) -> pd.DataFrame:
    """Full RFM segmentation pipeline."""
    if df is None:
        df = load_data()

    rfm = compute_rfm(df)
    rfm = score_rfm(rfm)
    rfm = assign_segment(rfm)

    # Save segmentation results
    os.makedirs(os.path.dirname(SEG_OUT_PATH), exist_ok=True)
    rfm.to_csv(SEG_OUT_PATH, index=False)
    logger.info(f"Segmentation results saved → {SEG_OUT_PATH}")

    # Generate visualisations
    plot_segment_distribution(rfm)
    plot_rfm_scatter(rfm)
    plot_rfm_boxplots(rfm)
    plot_segment_revenue(rfm)

    return rfm


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")
    run_segmentation()
