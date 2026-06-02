-- ============================================================
-- E-Commerce Analytics Platform — Database Schema
-- Engine: SQLite 3 (also compatible with MySQL/PostgreSQL)
-- ============================================================

-- ── Drop tables if re-initializing ────────────────────────
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS customer_summary;
DROP TABLE IF EXISTS rfm_segments;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS monthly_revenue;

-- ── Transactions (main fact table) ────────────────────────
CREATE TABLE transactions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    InvoiceNo     TEXT        NOT NULL,
    StockCode     TEXT        NOT NULL,
    Description   TEXT,
    Quantity      INTEGER     NOT NULL,
    InvoiceDate   DATETIME    NOT NULL,
    UnitPrice     REAL        NOT NULL CHECK (UnitPrice > 0),
    CustomerID    TEXT        NOT NULL,
    Country       TEXT        NOT NULL,
    Revenue       REAL        GENERATED ALWAYS AS (ROUND(Quantity * UnitPrice, 2)) STORED,
    OrderYear     INTEGER,
    OrderMonth    INTEGER,
    OrderDay      INTEGER,
    YearMonth     TEXT
);

-- ── Customer Summary (aggregated per customer) ─────────────
CREATE TABLE customer_summary (
    CustomerID      TEXT    PRIMARY KEY,
    TotalRevenue    REAL,
    TotalOrders     INTEGER,
    TotalItems      INTEGER,
    AvgOrderValue   REAL,
    FirstPurchase   DATETIME,
    LastPurchase    DATETIME,
    TenureDays      INTEGER,
    Country         TEXT
);

-- ── RFM Segments ──────────────────────────────────────────
CREATE TABLE rfm_segments (
    CustomerID      TEXT    PRIMARY KEY,
    Recency         INTEGER,
    Frequency       INTEGER,
    Monetary        REAL,
    R_Score         INTEGER,
    F_Score         INTEGER,
    M_Score         INTEGER,
    RFM_Score       INTEGER,
    RFM_Segment_Code TEXT,
    Segment         TEXT
);

-- ── Indexes for query performance ─────────────────────────
CREATE INDEX IF NOT EXISTS idx_tx_customer    ON transactions (CustomerID);
CREATE INDEX IF NOT EXISTS idx_tx_date        ON transactions (InvoiceDate);
CREATE INDEX IF NOT EXISTS idx_tx_stock       ON transactions (StockCode);
CREATE INDEX IF NOT EXISTS idx_tx_country     ON transactions (Country);
CREATE INDEX IF NOT EXISTS idx_tx_yearmonth   ON transactions (YearMonth);
CREATE INDEX IF NOT EXISTS idx_rfm_segment    ON rfm_segments (Segment);
