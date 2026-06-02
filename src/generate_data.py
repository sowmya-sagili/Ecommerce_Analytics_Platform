"""
E-Commerce Customer & Revenue Analytics Platform
=================================================
Synthetic Dataset Generator

Generates a realistic e-commerce dataset with intentional dirty data
(missing values, duplicates, negative quantities, invalid prices)
to demonstrate data cleaning capabilities.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# ─── Reproducibility ──────────────────────────────────────────────────────────
np.random.seed(42)
random.seed(42)

# ─── Constants ────────────────────────────────────────────────────────────────
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "ecommerce_data.csv")

COUNTRIES = [
    "United Kingdom", "Germany", "France", "Australia", "Netherlands",
    "Spain", "Switzerland", "Belgium", "Sweden", "Japan", "Norway",
    "Denmark", "Finland", "Italy", "Portugal", "USA", "Canada", "Singapore"
]

COUNTRY_WEIGHTS = [
    0.40, 0.08, 0.07, 0.05, 0.05,
    0.04, 0.04, 0.03, 0.03, 0.03, 0.03,
    0.02, 0.02, 0.02, 0.02, 0.03, 0.02, 0.02
]

PRODUCTS = [
    ("84406B", "CREAM CUPID HEARTS COAT HANGER",        2.95),
    ("84029G", "KNITTED UNION FLAG HOT WATER BOTTLE",   3.39),
    ("85123A", "WHITE HANGING HEART T-LIGHT HOLDER",    2.55),
    ("22423",  "REGENCY CAKESTAND 3 TIER",              12.75),
    ("47566",  "PARTY BUNTING",                          4.95),
    ("20725",  "LUNCH BAG RED RETROSPOT",                1.65),
    ("22720",  "SET OF 3 CAKE TINS PANTRY DESIGN",       4.95),
    ("23084",  "RABBIT NIGHT LIGHT",                     1.69),
    ("85099B", "JUMBO BAG RED RETROSPOT",                1.65),
    ("21212",  "PACK OF 72 RETROSPOT CAKE CASES",        0.55),
    ("22197",  "SMALL POPCORN HOLDER",                   0.72),
    ("23355",  "HOT WATER BOTTLE KEEP CALM",             4.65),
    ("22469",  "HEART OF WICKER SMALL",                  1.45),
    ("21930",  "JUMBO STORAGE BAG SUKI",                 2.08),
    ("22900",  "SET 2 TEA TOWELS I LOVE LONDON",         2.95),
    ("20727",  "LUNCH BAG BLACK SKULL",                  1.65),
    ("21929",  "JUMBO BAG PINK POLKADOT",                1.65),
    ("23203",  "LUNCH BAG APPLE DESIGN",                 1.65),
    ("22726",  "ALARM CLOCK BAKELIKE RED",               3.75),
    ("22629",  "SPACEBOY LUNCH BOX",                     1.95),
    ("21933",  "JUMBO BAG SCANDINAVIAN BLUE DAISY",      1.65),
    ("22197",  "SMALL POPCORN HOLDER",                   0.72),
    ("84997C", "RECYCLED ACRYLIC BEAD NECKLACE",         1.06),
    ("21258",  "VICTORIAN SEWING BOX LARGE",             7.95),
    ("22175",  "GIN + TONIC DIET METAL SIGN",            2.10),
    ("22457",  "NATURAL SLATE HEART CHALKBOARD",         2.10),
    ("22111",  "SCOTTIE DOG HOT WATER BOTTLE",           4.65),
    ("23209",  "LUNCH BAG GINGHAM DESIGN",               1.65),
    ("22086",  "PAPER CHAIN KIT CHRISTMAS DECORATIONS",  2.55),
    ("22616",  "PACK OF 12 LONDON TISSUES",              0.85),
    ("22632",  "HAND WARMER RED POLKA DOT",              2.10),
    ("21217",  "RED RETROSPOT MINI CASES",               0.85),
    ("21064",  "WOOD S/3 CABINET ANT WHITE",            16.95),
    ("22961",  "JAM MAKING SET PRINTED",                 1.45),
    ("21977",  "PACK OF 60 PINK PAISLEY CAKE CASES",     0.55),
    ("22144",  "FINISH LINE ENAMEL MUG",                 1.06),
    ("23166",  "MEDIUM CERAMIC TOP STORAGE JAR",         1.25),
    ("23228",  "SPACESHIP LAMP",                         2.55),
    ("20719",  "WOODLAND CHARLOTTE BAG",                 0.85),
    ("22382",  "LUNCH BOX WITH CUTLERY RETROSPOT",       2.55),
]

def generate_invoice_no(n: int) -> list:
    """Generate realistic invoice numbers (some shared = multi-item orders)."""
    unique_invoices = [f"C{536365 + i}" if random.random() < 0.02 else f"{536365 + i}"
                       for i in range(int(n * 0.45))]
    return [random.choice(unique_invoices) for _ in range(n)]


def generate_dates(n: int, start: str = "2022-01-01", end: str = "2023-12-31") -> list:
    start_dt = datetime.strptime(start, "%Y-%m-%d")
    end_dt   = datetime.strptime(end,   "%Y-%m-%d")
    delta    = (end_dt - start_dt).days
    # Seasonal boost: Q4 gets more orders
    dates = []
    for _ in range(n):
        d = start_dt + timedelta(days=random.randint(0, delta))
        # 30% chance of being bumped to Oct-Dec
        if random.random() < 0.30:
            d = d.replace(month=random.randint(10, 12),
                          day=random.randint(1, 28))
        dates.append(d.strftime("%Y-%m-%d %H:%M:%S"))
    return dates


def generate_dataset(n_rows: int = 10000) -> pd.DataFrame:
    """Generate a synthetic e-commerce dataset with realistic dirty data."""
    
    products_sample = [random.choice(PRODUCTS) for _ in range(n_rows)]
    stock_codes  = [p[0] for p in products_sample]
    descriptions = [p[1] for p in products_sample]
    unit_prices  = [round(p[2] * random.uniform(0.8, 1.2), 2) for p in products_sample]

    customer_pool = [f"{10000 + i}" for i in range(1500)]
    customer_ids  = [random.choice(customer_pool) for _ in range(n_rows)]
    
    quantities = np.random.randint(1, 50, size=n_rows).tolist()

    df = pd.DataFrame({
        "InvoiceNo":   generate_invoice_no(n_rows),
        "StockCode":   stock_codes,
        "Description": descriptions,
        "Quantity":    quantities,
        "InvoiceDate": generate_dates(n_rows),
        "UnitPrice":   unit_prices,
        "CustomerID":  customer_ids,
        "Country":     random.choices(COUNTRIES, weights=COUNTRY_WEIGHTS, k=n_rows),
    })

    # ── Inject dirty data (~20%) ──────────────────────────────────────────────
    dirty_pct = int(n_rows * 0.20)

    # Missing CustomerIDs (~8%)
    null_idx = random.sample(range(n_rows), int(n_rows * 0.08))
    df.loc[null_idx, "CustomerID"] = np.nan

    # Missing Descriptions (~3%)
    desc_idx = random.sample(range(n_rows), int(n_rows * 0.03))
    df.loc[desc_idx, "Description"] = np.nan

    # Negative quantities (returns, ~4%)
    neg_idx = random.sample(range(n_rows), int(n_rows * 0.04))
    df.loc[neg_idx, "Quantity"] = -df.loc[neg_idx, "Quantity"]

    # Zero or negative unit prices (~2%)
    price_idx = random.sample(range(n_rows), int(n_rows * 0.02))
    df.loc[price_idx, "UnitPrice"] = random.choices([-0.01, 0.0], k=len(price_idx))

    # Duplicate rows (~3%)
    dup_idx = random.sample(range(n_rows), int(n_rows * 0.03))
    duplicates = df.iloc[dup_idx].copy()
    df = pd.concat([df, duplicates], ignore_index=True)

    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    return df


if __name__ == "__main__":
    print("Generating synthetic e-commerce dataset...")
    df = generate_dataset(10000)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Dataset saved: {OUTPUT_PATH}")
    print(f"Shape: {df.shape}")
    print(df.head())
