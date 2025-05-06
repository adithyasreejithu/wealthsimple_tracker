import re 
import sqlite3

# database = sqlite3.connect("wealthsimple.db")
# cursor = database.cursor()
trans_acc = ["Div","Buy","Cont","Lend"]


def pull_stock_id(ticker, company):
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
            cursor.execute("INSERT INTO Stocks (Ticker, Company) VALUES (?, ?)",(ticker, company))
            connection.commit()
            return cursor.lastrowid
    

# def add (stock, company):
    

def add_nine(stock_id,date, trans_type, edate, shares, fx_rate, amount1, amount2, amount3): 
     with sqlite3.connect("wealthsimple.db") as connection:
          cursor = connection.cursor()
          cursor.execute("""INSERT OR IGNORE INTO Transactions (Stock_ID, Date, Type, Executed_Date, Shares, Fx_Rate, Value, Credit, Balance)
                         Values (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (stock_id, date, trans_type, edate, shares, fx_rate, amount1, amount2, amount3))
          connection.commit()


def add_five(date, trans_type, amount1, amount2, amount3):
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