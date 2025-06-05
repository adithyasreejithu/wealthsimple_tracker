import re
import sqlite3
import os
from dataclasses import dataclass

# database = sqlite3.connect("wealthsimple.db")
# cursor = database.cursor()
trans_acc = ["Div","Buy","Cont","Lend"]
database = os.getenv("DB_NAME")

# Functions for Pdf_reader.py
def pull_stock_id(ticker, company, exchange):
    """
    Ticker 
    Company
    """
    with sqlite3.connect("wealthsimple.db") as connection:
      cursor = connection.cursor()
      cursor.execute("SELECT id FROM Stocks WHERE Ticker = ?", (ticker,))
      stock_row = cursor.fetchone()

      if stock_row: 
            return stock_row[0]
      else : 
            cursor.execute("INSERT INTO Stocks (Ticker, Company, Exchange) VALUES (?, ?, ?)",(ticker, company, exchange))
            connection.commit()
            return cursor.lastrowid
      

def add_nine(stock_id,date, trans_type, edate, shares, fx_rate, amount1, amount2, amount3):  # Need to be renamed
     with sqlite3.connect("wealthsimple.db") as connection:
          cursor = connection.cursor()
          cursor.execute("""INSERT OR IGNORE INTO Transactions (Stock_ID, Date, Type, Executed_Date, Shares, Fx_Rate, Value, Credit, Balance)
                         Values (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (stock_id, date, trans_type, edate, shares, fx_rate, amount1, amount2, amount3))
          connection.commit()


def add_five(date, trans_type, amount1, amount2, amount3): # Need to be renamed
    stock_id = 0 
    executed_date = date
    shares = 0
    fx_rate = 0

    with sqlite3.connect("wealthsimple.db") as connection:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO Transactions 
            (Stock_ID, Type, Date, Executed_Date, Shares, Fx_Rate, Value, Credit, Balance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (stock_id, trans_type, date, executed_date, shares, fx_rate, amount1, amount2, amount3))
        connection.commit()
    


# Functions for gather_stock_history.py
def get_tickers():
    """
    Will Return full list of all tickers in the specified database
    """
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()

        statement = """
            SELECT ticker, exchange FROM Stocks;
        """

        cursor.execute(statement)
        fetch = cursor.fetchall()
        # tick_list = [ticker[0] for ticker in fetch]
        return fetch

def get_exchange(ticker):
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()

        statement = """
            SELECT ticker, exchange FROM Stocks
            WHERE ticker = ?;
        """

        cursor.execute(statement, (ticker,))
        fetch = cursor.fetchall()
        # tick_list = [ticker[0] for ticker in fetch]
        return fetch

def hist_database_check():
    """
    Retrives historical stock data from the database
    """
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()

        statement = """
            SELECT 
                History.Date,
                History.Open,
                History.Close,
                History.Adj_close,
                History.High,
                History.Low, 
                History.Daily_change
            FROM History
            INNER JOIN Stocks ON History.Stock_ID = Stocks.id
            ORDER BY History.Date ASC;
        """

        cursor.execute(statement)
        fetch = cursor.fetchall()
        return fetch
    
@dataclass
class InvestmentSummary: 
    total_share: float 
    cad_total : float
    usd_total : float 
    total_div : float 

def get_investment_summary(ticker: str) -> InvestmentSummary:
    with sqlite3.connect("wealthsimple.db") as connection: 
        cursor = connection.cursor()

        total_shares_sql = """
            SELECT 
            SUM(Transactions.Shares) AS shares_total
            FROM Transactions
            INNER JOIN Stocks ON Transactions.Stock_ID = Stocks.id
            WHERE Type = "Buy" AND Stocks.Ticker = ?;
        """
        cursor.execute(total_shares_sql, (ticker,))
        total_shares = cursor.fetchone()[0]

        cost_basis_sql = """
            SELECT 
            Transactions.Shares,
            Transactions.Fx_Rate,
            Transactions.Value
            FROM Transactions
            INNER JOIN Stocks ON Transactions.Stock_ID = Stocks.id
            WHERE Type = "Buy" AND Stocks.Ticker = ?
            ORDER BY Transactions.Date ASC;
        """
        cursor.execute(cost_basis_sql, (ticker,))
        cost_basis = cursor.fetchall()

        cad_total = 0 
        usd_total = 0

        for shares, fx_rate, value in cost_basis:
            if not fx_rate:
                cad_total += value
            else:
                usd_total += value / fx_rate
        
        dividends_sql = """
            SELECT 
            SUM(Transactions.Credit)
            FROM Transactions
            INNER JOIN Stocks ON Transactions.Stock_ID = Stocks.id
            WHERE Type = "Dividend" AND Stocks.Ticker = ?;
        """
        cursor.execute(dividends_sql, (ticker,))
        total_div = cursor.fetchall()[0]

    return InvestmentSummary(
        total_share= total_shares,
        cad_total= cad_total,
        usd_total= usd_total,
        total_div= total_div
    )

def dateframe_to_db(df): 
    connection = sqlite3.connect("wealthsimple.db")
    df.to_sql("History", connection, if_exists="append", index=False)
    connection.close()

    
def get_securities_last_date():
    with sqlite3.connect("wealthsimple.db") as connection :
        cursor = connection.cursor()
        query = """
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
        """
    cursor.execute(query)
    fetch = cursor.fetchall()
    return fetch