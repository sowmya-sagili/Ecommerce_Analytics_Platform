-- ============================================================
-- E-Commerce Analytics Platform — Analysis Queries
-- Optimized SQL for common business analytics questions
-- Compatible with SQLite 3 and MySQL 8+
-- ============================================================

-- ────────────────────────────────────────────────────────────
-- 1. TOP 10 CUSTOMERS BY LIFETIME REVENUE
-- ────────────────────────────────────────────────────────────
SELECT
    t.CustomerID,
    cs.Country,
    COUNT(DISTINCT t.InvoiceNo)     AS TotalOrders,
    SUM(t.Quantity)                  AS TotalItemsBought,
    ROUND(SUM(t.Revenue), 2)         AS LifetimeRevenue,
    ROUND(AVG(t.Revenue), 2)         AS AvgOrderRevenue,
    MIN(t.InvoiceDate)               AS FirstPurchase,
    MAX(t.InvoiceDate)               AS LastPurchase
FROM transactions t
LEFT JOIN customer_summary cs ON t.CustomerID = cs.CustomerID
GROUP BY t.CustomerID, cs.Country
ORDER BY LifetimeRevenue DESC
LIMIT 10;


-- ────────────────────────────────────────────────────────────
-- 2. TOP 20 PRODUCTS BY TOTAL REVENUE
-- ────────────────────────────────────────────────────────────
SELECT
    StockCode,
    Description,
    COUNT(DISTINCT InvoiceNo)        AS TotalOrders,
    SUM(Quantity)                     AS TotalUnitsSold,
    ROUND(AVG(UnitPrice), 2)          AS AvgUnitPrice,
    ROUND(SUM(Revenue), 2)            AS TotalRevenue
FROM transactions
GROUP BY StockCode, Description
ORDER BY TotalRevenue DESC
LIMIT 20;


-- ────────────────────────────────────────────────────────────
-- 3. MONTHLY REVENUE SUMMARY
-- ────────────────────────────────────────────────────────────
SELECT
    YearMonth,
    COUNT(DISTINCT InvoiceNo)         AS TotalOrders,
    COUNT(DISTINCT CustomerID)        AS UniqueCustomers,
    SUM(Quantity)                      AS TotalItemsSold,
    ROUND(SUM(Revenue), 2)             AS MonthlyRevenue,
    ROUND(AVG(Revenue), 2)             AS AvgOrderRevenue
FROM transactions
GROUP BY YearMonth
ORDER BY YearMonth;


-- ────────────────────────────────────────────────────────────
-- 4. COUNTRY-WISE REVENUE ANALYSIS
-- ────────────────────────────────────────────────────────────
SELECT
    Country,
    COUNT(DISTINCT CustomerID)         AS UniqueCustomers,
    COUNT(DISTINCT InvoiceNo)          AS TotalOrders,
    ROUND(SUM(Revenue), 2)              AS TotalRevenue,
    ROUND(AVG(Revenue), 2)              AS AvgOrderValue,
    ROUND(SUM(Revenue) * 100.0 /
          (SELECT SUM(Revenue) FROM transactions), 2) AS RevenueSharePct
FROM transactions
GROUP BY Country
ORDER BY TotalRevenue DESC;


-- ────────────────────────────────────────────────────────────
-- 5. CUSTOMER LIFETIME VALUE (CLV)
-- ────────────────────────────────────────────────────────────
SELECT
    cs.CustomerID,
    cs.Country,
    cs.TotalOrders,
    cs.TotalRevenue                              AS CLV,
    cs.AvgOrderValue,
    cs.TenureDays,
    CASE
        WHEN cs.TenureDays > 0
        THEN ROUND(cs.TotalRevenue / (cs.TenureDays / 30.0), 2)
        ELSE 0
    END                                           AS MonthlyValueRate,
    COALESCE(r.Segment, 'Unscored')               AS RFM_Segment
FROM customer_summary cs
LEFT JOIN rfm_segments r ON cs.CustomerID = r.CustomerID
ORDER BY CLV DESC
LIMIT 50;


-- ────────────────────────────────────────────────────────────
-- 6. REPEAT CUSTOMERS (purchased more than once)
-- ────────────────────────────────────────────────────────────
SELECT
    CustomerID,
    Country,
    TotalOrders,
    TotalRevenue,
    FirstPurchase,
    LastPurchase,
    TenureDays
FROM customer_summary
WHERE TotalOrders > 1
ORDER BY TotalOrders DESC;


-- ────────────────────────────────────────────────────────────
-- 7. AVERAGE ORDER VALUE BY MONTH
-- ────────────────────────────────────────────────────────────
SELECT
    YearMonth,
    COUNT(DISTINCT InvoiceNo)              AS TotalOrders,
    ROUND(SUM(Revenue), 2)                  AS TotalRevenue,
    ROUND(SUM(Revenue) /
          COUNT(DISTINCT InvoiceNo), 2)     AS AvgOrderValue
FROM transactions
GROUP BY YearMonth
ORDER BY YearMonth;


-- ────────────────────────────────────────────────────────────
-- 8. RFM SEGMENT ANALYSIS SUMMARY
-- ────────────────────────────────────────────────────────────
SELECT
    r.Segment,
    COUNT(r.CustomerID)              AS CustomerCount,
    ROUND(AVG(r.Recency), 1)         AS AvgRecencyDays,
    ROUND(AVG(r.Frequency), 1)       AS AvgOrderFrequency,
    ROUND(AVG(r.Monetary), 2)        AS AvgMonetaryValue,
    ROUND(SUM(r.Monetary), 2)        AS TotalSegmentRevenue,
    ROUND(AVG(r.RFM_Score), 1)       AS AvgRFMScore
FROM rfm_segments r
GROUP BY r.Segment
ORDER BY TotalSegmentRevenue DESC;


-- ────────────────────────────────────────────────────────────
-- 9. DAY-OF-WEEK REVENUE PATTERN
-- ────────────────────────────────────────────────────────────
SELECT
    OrderDayOfWeek,
    COUNT(DISTINCT InvoiceNo)         AS TotalOrders,
    ROUND(SUM(Revenue), 2)             AS TotalRevenue,
    ROUND(AVG(Revenue), 2)             AS AvgOrderValue
FROM transactions
GROUP BY OrderDayOfWeek
ORDER BY TotalRevenue DESC;


-- ────────────────────────────────────────────────────────────
-- 10. PRODUCTS NEVER PURCHASED IN LAST 90 DAYS (Slow Movers)
-- ────────────────────────────────────────────────────────────
SELECT
    StockCode,
    Description,
    ROUND(SUM(Revenue), 2)             AS TotalRevenue,
    MAX(InvoiceDate)                   AS LastSaleDate,
    JULIANDAY('now') - JULIANDAY(MAX(InvoiceDate)) AS DaysSinceLastSale
FROM transactions
GROUP BY StockCode, Description
HAVING DaysSinceLastSale > 90
ORDER BY DaysSinceLastSale DESC
LIMIT 30;
