-- ============================================================
-- E-Commerce Analytics Platform — Data Import
-- Imports data from CSV files into the SQLite database
-- Run after schema.sql
-- ============================================================

-- NOTE: SQLite .import requires the sqlite3 CLI.
-- The Python pipeline (dashboard_data_generator.py) handles
-- this automatically via pandas .to_sql().
-- These statements are provided for manual CLI import.

-- ── Step 1: Set CSV mode and import transactions ───────────
-- .mode csv
-- .headers on
-- .import data/processed/cleaned_data.csv transactions

-- ── Step 2: Import customer summary ───────────────────────
-- .import data/processed/customer_summary.csv customer_summary

-- ── Step 3: Import RFM segments ───────────────────────────
-- .import data/processed/rfm_segments.csv rfm_segments

-- ── Verify row counts ─────────────────────────────────────
SELECT 'transactions'    AS table_name, COUNT(*) AS row_count FROM transactions
UNION ALL
SELECT 'customer_summary',              COUNT(*)               FROM customer_summary
UNION ALL
SELECT 'rfm_segments',                  COUNT(*)               FROM rfm_segments;
