import sqlite3

database = sqlite3.connect("wealthsimple.db")  # creating db if it doesnt exist 
cursor = database.cursor() # object to interact with the database 

"""
Create db with following column headers: 

PDF Columns: date, type, Name, Quantity, value, Credit, Balance

Query Dividends: Date, Ticker, Company, Desc, recv_date, Value, Credit, Balance
Query Buy: Date, Ticker, Desc, Bought, edate, Fx_rate, Value, Credit, Balance
Query Contributions: Date, value, Credit, Balance
Query Lending: Date, Value, Credit, Balance
"""

# Creating Database Schema
cursor.execute('''
CREATE TABLE IF NOT EXISTS Stocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Ticker TEXT UNIQUE NOT NULL,
    Company TEXT NOT NULL,
    Exchange TEXT NOT NULL
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Transactions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Stock_ID INTEGER NOT NULL,
    Date TEXT NOT NULL, 
    Type TEXT CHECK (Type IN ('Buy', 'Sell', 'Dividend', 'Contribution', 'Lending')),
    Executed_Date TEXT NOT NULL,
    Shares REAL,
    Fx_Rate REAL, 
    Value REAL NOT NULL,
    Credit REAL NOT NULL,
    Balance REAL NOT NULL,
    FOREIGN KEY (Stock_ID) REFERENCES Stocks(id) ON DELETE CASCADE,
    UNIQUE (Stock_ID, Type, Date, Executed_Date, Value, Credit, Balance),
    CHECK (
        (Type IN ('Contribution', 'Lending') AND Stock_ID = 0)
        OR (Type NOT IN ('Contribution', 'Lending') AND Stock_ID != 0)
    )

);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS History (
    id INTEGER PRIMARY KEY AUTOINCREMENT,    -- Unique row ID
    Date TEXT NOT NULL,                      -- Trading date (YYYY-MM-DD)
    Stock_ID INTEGER NOT NULL,               -- Foreign key to Stocks table
    Open REAL NOT NULL,                      -- Opening price of stock on this date
    Close REAL NOT NULL,                     -- Closing price of stock on this date
    Adj_close REAL NOT NULL,                 -- Adjusted close price
    High REAL NOT NULL,                      -- Highest price on this date
    Low REAL NOT NULL,                       -- Lowest price on this date
    Book_Cost REAL NOT NULL,                 -- Average purchase price per share 
    Shares INTEGER NOT NULL,                 -- Number of shares held
    Total_Value REAL,                        -- Market value of holding
    Unreal_Gains REAL,                       -- Unrealized gains/losses
    Daily_Change REAL,                       -- Daily change vs. book cost
    Moving_Avg_20D REAL,                     -- 20-day moving average
    Volatility_20D REAL,                     -- 20-day rolling volatility
    Expo_Moving_Average_20D REAL,            -- 20-day exponential moving average
    FOREIGN KEY (Stock_ID) REFERENCES Stocks(id) ON DELETE CASCADE,
    UNIQUE (Date, Stock_ID)                  
);
''')

# Commit changes and close database
database.commit()
database.close()

# Ticker, Company 
# Stock_ID, Date, Type, Executed_Date, Shares, Fx_Rate, Value, Credit, Balance