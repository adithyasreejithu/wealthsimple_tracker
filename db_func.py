import re
import sqlite3
import os
import pandas as pd
from dataclasses import dataclass

# database = sqlite3.connect("wealthsimple.db")
# cursor = database.cursor()
trans_acc = ["Div","Buy","Cont","Lend"]
database = os.getenv("DB_NAME")

# Functions for Pdf_reader.py
def pull_stock_id(ticker, company, exchange):
    """
    Retrieves the stock ID from the database if it exists; otherwise inserts and returns new ID.
    """
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM Stocks WHERE Ticker = ?", (ticker,))
        stock_row = cursor.fetchone()

        if stock_row:
            return stock_row[0]
        else:
            cursor.execute(
                "INSERT INTO Stocks (Ticker, Company, Exchange) VALUES (?, ?, ?)",
                (ticker, company, exchange)
            )
            connection.commit()
            return cursor.lastrowid

def add_five(date, trans_type, amount1, amount2, amount3):
    """
    Inserts a transaction record with only 5 inputs; used for general transfers or no-security entries.
    """
    stock_id = 0
    executed_date = date
    shares = 0
    fx_rate = 0

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO Transactions 
            (Stock_ID, Type, Date, Executed_Date, Shares, Fx_Rate, Value, Credit, Balance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (stock_id, trans_type, date, executed_date, shares, fx_rate, amount1, amount2, amount3))
        connection.commit()

def add_nine(stock_id, date, trans_type, edate, shares, fx_rate, amount1, amount2, amount3):
    """
    Inserts a transaction record with all fields populated.
    """
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO Transactions 
            (Stock_ID, Date, Type, Executed_Date, Shares, Fx_Rate, Value, Credit, Balance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (stock_id, date, trans_type, edate, shares, fx_rate, amount1, amount2, amount3))
        connection.commit()


# Functions for gather_stock_history.py
def hist_database_check():
    """
    Retrieves all historical stock data from the History table.
    """
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT 
                History.Date,
                History.Open,
                History.Close,
                History.Adj_close,
                History.High,
                History.Low
            FROM History
            INNER JOIN Stocks ON History.Stock_ID = Stocks.id
            ORDER BY History.Date ASC;
        """)
        return cursor.fetchall()

def dateframe_to_db(df):
    """
    Appends a DataFrame to the History table in the database.
    """
    connection = sqlite3.connect(database)
    df.to_sql("History", connection, if_exists="append", index=False)
    connection.close()

def get_tickers():
    """
    Returns full list of all tickers and their exchanges from the database.
    """
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT ticker, exchange FROM Stocks;")
        return cursor.fetchall()

def get_exchange(ticker):
    """
    Returns ticker and exchange for a given ticker symbol.
    """
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT ticker, exchange FROM Stocks
            WHERE ticker = ?;
        """, (ticker,))
        return cursor.fetchall()
    
@DeprecationWarning
def get_securities_last_date():
    """
    Gets the most recent historical entry for each stock.
    """
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute("""
            WITH RankedHistory AS (
                SELECT
                    Stock_ID,
                    Date,
                    ROW_NUMBER() OVER (PARTITION BY Stock_ID ORDER BY Date DESC) AS rn
                FROM History
            )
            SELECT
                s.Ticker,
                r.Date
            FROM RankedHistory r
            INNER JOIN Stocks s ON r.Stock_ID = s.id
            WHERE r.rn = 1;
        """)
        return cursor.fetchall()

def get_ticker_last_date_history(ticker):
    """
    Gets the the securities most recent API entry from the History Database for the specified stock
    """
    with sqlite3.connect(database) as connection: 
        cursor = connection.cursor()
        cursor.execute("""
            SELECT
                History.Date
            FROM History
            INNER JOIN Stocks ON History.Stock_ID = Stocks.id
            WHERE Stocks.Ticker = ?
            ORDER BY History.Date DESC
            LIMIT 1;
        """,(ticker,))
        return cursor.fetchone()

# def get_ticker_purchase_history(ticker):
#     """
#     Gets the securities buying history 
#     """
#     with sqlite3.connect(database) as connection:
#         cursor = connection.cursor()
#         cursor.execute("""
#             SELECT
#                 Transactions.Executed_Date, 
#                 Transactions.Type, 
#                 Transactions.Fx_Rate,
#                 Transactions.Shares, 
#                 Transactions.Value,
#                 Transactions.Credit 
#             FROM Transactions
#             INNER JOIN Stocks ON Transactions.Stock_ID = Stocks.id
#             WHERE Stocks.Ticker = "PZA"
#             -- AND (Type = 'Buy' OR Type = 'Dividend') -- This needs to be changed to reinvested dividends 
#                 AND (Transactions.Type = 'Buy')
#             ORDER BY Executed_Date ASC;
#         """, (ticker,))


@dataclass
class StockDataBundle: 
    purchases: pd.DataFrame
    history: pd.DataFrame

def get_stock_data_bundle(ticker: int) -> StockDataBundle:
    """
    This return a S"""
    with sqlite3.connect(database) as connection : 
        get_buys = """
            SELECT
                Transactions.Executed_Date, 
                Transactions.Type, 
                Transactions.Fx_Rate,
                Transactions.Shares, 
                Transactions.Value,
                Transactions.Credit 
            FROM Transactions
            INNER JOIN Stocks ON Transactions.Stock_ID = Stocks.id
            WHERE Stocks.Ticker = ?
            -- AND (Type = 'Buy' OR Type = 'Dividend') -- This needs to be changed to reinvested dividends 
                AND (Transactions.Type = 'Buy')
            ORDER BY Executed_Date ASC;
        """
        get_dates = """
            SELECT 
                History.Date,
                History.Open, 
                History.Close,
                History.Adj_close,
                History.Low
            FROM History
            INNER JOIN Stocks ON History.Stock_ID = Stocks.id
            WHERE Stocks.Ticker = ?;
        """

    stock_pur = pd.read_sql_query(get_buys,connection,params=(ticker[0],)) # These are the purchase dates 
    stocks_hist = pd.read_sql_query(get_dates,connection,params=(ticker[0],)) # This the dates stored in the database
    return StockDataBundle(purchases=stock_pur, history=stocks_hist) 


# Functions for Streamlit 
@dataclass
class InvestmentSummary:
    total_share: float
    cad_total: float
    usd_total: float
    total_div: float
    port_percent: float 

def get_investment_summary(ticker: str, date1: str, date2: str) -> InvestmentSummary:
    """
    Returns total shares, CAD and USD cost basis, and total dividends for a ticker.
    """
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()

        # Total shares
        cursor.execute("""
            SELECT 
                SUM(Transactions.Shares) AS shares_total
            FROM Transactions
            INNER JOIN Stocks ON Transactions.Stock_ID = Stocks.id
            WHERE Type = 'Buy' 
                AND Stocks.Ticker = ?
                AND Transactions.Date > ?
                AND Transactions.Date < ?;
        """, (ticker,date1, date2))
        total_shares = cursor.fetchone()[0] or 0

        # Cost basis
        cursor.execute("""
            SELECT
                Transactions.Shares,
                Transactions.Fx_Rate,
                Transactions.Value
            FROM Transactions
            INNER JOIN Stocks ON Transactions.Stock_ID = Stocks.id
            WHERE Type = 'Buy' 
                AND Stocks.Ticker = ?
                AND Transactions.Date > ?
                AND Transactions.Date < ?
            ORDER BY Transactions.Date ASC;

        """, (ticker,date1, date2))
        cost_basis = cursor.fetchall()

        cad_total = 0
        usd_total = 0
        for shares, fx_rate, value in cost_basis:
            if not fx_rate:
                cad_total += value
            else:
                usd_total += value / fx_rate

        # Dividends
        cursor.execute("""
            SELECT 
                SUM(Transactions.Credit)
            FROM Transactions
            INNER JOIN Stocks ON Transactions.Stock_ID = Stocks.id
            WHERE Type = "Dividend" 
                AND Stocks.Ticker = ?
                AND Transactions.Date > ?
                AND Transactions.Date < ?;
                    """, (ticker, date1, date2))
        total_div = cursor.fetchone()[0]

        with sqlite3.connect(database) as connection: 
            cursor = connection.cursor()
            query = """
            WITH LastExchange AS (
            SELECT
                Stock_ID,
                Total_Value,
                ROW_NUMBER() OVER (PARTITION BY Stock_ID ORDER BY Date DESC) AS LE
            FROM History
            WHERE Date < ?
            ) 
            SELECT
                Stocks.Ticker,
                LastExchange.Total_Value
            FROM LastExchange 
            INNER JOIN Stocks ON LastExchange.Stock_ID = Stocks.id
            WHERE LastExchange.LE = 1;
            """
            value = pd.read_sql_query(query,connection,params=(date2,))
            total_value = value["Total_Value"].sum()

            for num, tick in enumerate(value["Ticker"]): 
                if tick == ticker:
                    tick_value = value.loc[num, 'Total_Value']
            
            port_percent = tick_value/total_value
            form_port_percent = "{:.2f}".format(port_percent)

            
        return InvestmentSummary(
            total_share=total_shares or 0,
            cad_total=cad_total,
            usd_total=usd_total,
            total_div=total_div or 0,
            port_percent=form_port_percent or 0

        )
    
def get_graph_date(tick, start_date, end_date):
    with sqlite3.connect(database) as connection: 
        query = """
        SELECT 
        History.Date, 
        History.Adj_close,
        History.Book_Cost
        FROM History
        INNER JOIN Stocks ON History.Stock_ID = Stocks.id
        WHERE Stocks.Ticker = ?
            AND History.Date > ?
            AND History.Date < ?
        ORDER BY History.Date  ASC;
        """

    graph_data = pd.read_sql_query(query,connection, params=(tick,start_date,end_date))

    return graph_data

    