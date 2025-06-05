-- SQLite
-- This shows the list query of everythings inside this database 
-- SELECT id, Stock_ID, Date, Type, Executed_Date, Shares, Fx_Rate, Value, Credit, Balance
-- FROM Transactions
-- -- WHERE Date >= "2024-12-12"
-- --     AND Date <= "2024-12-31"
-- --     AND type = "Dividend"
-- -- ORDER BY date ASC
-- WHERE type = "Buy"
-- ORDER BY date ASC
-- ;


-- This shows the the total of the values 
SELECT 
    Transactions.id AS transaction_id,
    Stocks.Ticker,
    Transactions.Date,
    Transactions.Type,
    -- Transactions.Executed_Date,
    -- SUM (Transactions.Shares) as shares_total,
    Transactions.Shares,
    Transactions.Fx_Rate,
    Transactions.Value,
    Transactions.Credit
FROM Transactions
INNER JOIN Stocks ON Transactions.Stock_ID = Stocks.id
WHERE Type = "Dividend" AND Stocks.Ticker = "VFV"
ORDER BY Transactions.Date ASC;


-- THIS SHOWS THE TOTAL AMOUNT OF A SHARE I OWN 
-- SELECT 
--     SUM(Transactions.Shares) AS shares_total
-- FROM Transactions
-- INNER JOIN Stocks ON Transactions.Stock_ID = Stocks.id
-- WHERE Type = "Buy" AND Stocks.Ticker = "VFV";

-- SELECT 
--     SUM (Transactions.Credit)
-- FROM Transactions
-- INNER JOIN Stocks ON Transactions.Stock_ID = Stocks.id
-- WHERE Type = "Dividend" AND Stocks.Ticker = "T"
-- ORDER BY Transactions.Date ASC;


-- SELECT Ticker FROM Stocks; 

-- SELECT 
--     History.Date,
--     History.Open,
--     History.Close,
--     History.Adj_close,
--     History.High,
--     History.Low, 
--     History.Daily_change
-- FROM History
-- INNER JOIN Stocks ON History.Stock_ID = Stocks.id
-- ORDER BY History.Date ASC;


-- DROP TABLE History;


-- CREATE TABLE IF NOT EXISTS History (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     Date TEXT NOT NULL,
--     Stock_ID INTEGER NOT NULL, 
--     Open REAL NOT NULL,
--     Close REAL NOT NULL,
--     Adj_close REAL NOT NULL,
--     High  REAL NOT NULL,
--     Low REAL NOT NULL,
--     Daily_change REAL NOT NULL,
--     FOREIGN KEY (Stock_ID) REFERENCES Stocks(id) ON DELETE CASCADE,
--     UNIQUE (Date, Stock_ID, Open, Adj_close, High, Low, Daily_change)
--     );

-- SELECT
--     Stock_ID,
--     Date
-- FROM History
-- -- WHERE Date > "2025-05-07"
-- ORDER BY Date DESC
-- LIMIT 1;

-- WITH RankedHistory AS (
--     SELECT
--         Stock_ID,
--         Date,
--         ROW_NUMBER() OVER (PARTITION BY Stock_ID ORDER BY Date DESC) AS rn
--     FROM History
-- )
-- SELECT
--     Stock_ID,
--     Date
-- FROM RankedHistory
-- WHERE rn = 1;


-- SELECT Ticker FROM Stocks
-- WHERE id = "1";



-- WITH RankedHistory AS (
--     SELECT
--         Stock_ID,
--         Date,
--         ROW_NUMBER() OVER (PARTITION BY Stock_ID ORDER BY Date DESC) AS rn
--     FROM History
-- )
-- SELECT
--     s.Ticker,
--     r.Date
-- FROM RankedHistory r
-- INNER JOIN Stocks s ON r.Stock_ID = s.id
-- WHERE r.rn = 1;

-- 
-- 
--  PORTFOLIO QUERIES --
-- 
-- 

-- This would be the query for the main page 
SELECT
    Date,
    Stock_ID,
    Daily_change
FROM History
ORDER BY Date ASC; 

SELECT
    Date,
    Stock_ID,
    Daily_change
FROM History
WHERE Stock_ID = 1
ORDER BY Date ASC; 




-- This would be used to mark the main portfolio Changes 
SELECT 
    Date,
    Type,
    Credit
    -- SUM (Credit) as Total_Cont
FROM Transactions
WHERE Type = "Contribution";

SELECT
    Executed_Date, 
    Type, 
    Fx_Rate, 
    Value 
FROM Transactions
WHERE Stock_ID = 3
  AND (Type = 'Buy' OR Type = 'Dividend')
ORDER BY Executed_Date ASC;


SELECT  
    Stocks.Ticker,
    COUNT(Stocks.Ticker = "VFV") as ticker.total,
    type, 
    Value 
    ticker.count 
FROM Transactions
INNER JOIN Stocks ON Transactions.Stock_ID = Stocks.id;


SELECT  
    Stocks.Ticker,
    Transactions.Stock_ID,
    COUNT(*) AS ticker_total
FROM Transactions
INNER JOIN Stocks ON Transactions.Stock_ID = Stocks.id
-- WHERE Stocks.Ticker = 'VFV'
GROUP BY Stocks.id
ORDER BY ticker_total DESC;


DROP TABLE Placeholder;




CREATE TABLE IF NOT EXISTS Placeholder (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique row ID
    Date TEXT NOT NULL,                     -- Trading date (YYYY-MM-DD)
    Stock_ID INTEGER NOT NULL,              -- Foreign key to Stocks table
    Open REAL NOT NULL,                     -- Opening price of stock on this date
    Close REAL NOT NULL,                    -- Closing price of stock on this date
    Adj_close REAL NOT NULL,                -- Adjusted close price (adjusted for splits/dividends)
    High REAL NOT NULL,                     -- Highest price on this date
    Low REAL NOT NULL,                      -- Lowest price on this date
    Book_Cost REAL NOT NULL,                -- Average purchase price per share 
    Shares INTEGER NOT NULL,                -- Number of shares held
    Total_Value REAL,                       -- Market value of holding on this date (Adj_close * Shares)
    Unreal_Gains REAL,                      -- Unrealized gain/loss (market value - book cost * shares)
    Volatility REAL,                       -- Rolling volatility (e.g., 20-day std dev of returns), nullable if not computable
    FOREIGN KEY (Stock_ID) REFERENCES Stocks(id) ON DELETE CASCADE,
    UNIQUE (Date, Stock_ID)                 -- Enforce unique stock data per stock and date
);





