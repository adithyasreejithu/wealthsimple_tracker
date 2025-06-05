import pandas as pd 
import yfinance as yf 
import db_func as func
from datetime import datetime, timedelta
from curl_cffi import requests

# Function to retrieve stock data 
def get_yfinance_data(ticker, start_date, end_date): # change the name to yfinace_to_db

    # Gets todays date for the API pull
   
    # Finds Canadian securities to fit API formats
    if ticker[1] == "Cad": # this will need to changed to CAD 
        suffix = ticker[0] + ".TO"
    else:
        suffix = ticker[0] 
    
    # Attempt to Pull API Data 
    try:
        # Create session that impersonates Chrome to avoid rate limit
        session = requests.Session(impersonate="chrome")

        # Use custom session with yfinance`                                                                     `
        stock = yf.Ticker(suffix, session=session)

        # Fetch stock history
        history = stock.history(start=start_date, end=end_date, interval="1d", auto_adjust=False)
        consol_his = ["Open", "Close","High", "Low", "Adj Close"]
        dataset = history[consol_his].copy()

        # Get Investment Information  
        summary = func.get_investment_summary(ticker[0])
        
        # Sorting Calculations based on exchange (currency Issues).
        
        if suffix.endswith(".TO"):
            book_cost = summary.cad_total/summary.total_share
        else :
            book_cost = summary.usd_total/summary.total_share

        # Formatting Stock data to pass to DB 
        stock_id = func.pull_stock_id(ticker[0], None, None)
        dataset["Stock_ID"] = stock_id
        dataset["Daily_change"] = dataset["Adj Close"] - book_cost
        dataset["Date"] = dataset.index.date
        dataset = dataset.rename(columns={"Adj Close": "Adj_close"})
        dataset = dataset[[
            "Date", "Stock_ID", "Open", "Close", "Adj_close", "High", "Low", "Daily_change"
        ]]
        func.dateframe_to_db(dataset)

    except Exception as e:
        # print("Failed to fetch data:")  # Will need to turn this into a logging function 
        return None

# Main functions 
tickers = func.get_tickers()
hist_data = func.hist_database_check()
tdy = datetime.today().strftime("%Y-%m-%d")
start_date = "2023-07-13" # This will need to be specifed by the user 


# If the database has no content
if hist_data == []: 
    for tick in tickers:    
        get_yfinance_data(tick, start_date, tdy) # this uses yfinance api to get stock data
        # sys.exit()

# If content exists within the database
else:
    # Now check of the database will need to occur to see how much data is in the database 
    date_query = func.get_securities_last_date()
    df = pd.DataFrame(date_query,columns=["ID", "Date"])
    df["Date"] = pd.to_datetime(df["Date"])
    tdy = datetime.today().strftime("%Y-%m-%d")
    filtered = df[df["Date"] < tdy]
    
    for _, row in df.iterrows():
        print(f'This is the id {row["ID"]} and this is the last date {row["Date"].strftime("%Y-%m-%d")}')
        value = func.get_exchange(row["ID"])
        # print(type(value))
        # print(row["Date"].strftime("%Y-%m-%d"))
        date_obj = datetime.strptime(row["Date"].strftime("%Y-%m-%d"), "%Y-%m-%d")  # Convert to datetime
        next_day = date_obj + timedelta(days=1)  # Without adding a day the unique constraint will be triggered 
        next_day_str = next_day.strftime("%Y-%m-%d") 
        get_yfinance_data(value[0], next_day_str, tdy)

    # Need to create a query that will read the last date of each stock_id to see if there is data on todays date 

    # Need to complete stock retrievial for the data 

    # There needs to be a case for when a new stock is added this would cross reference if all the stockids and history output match up




"""The syntax : 
    Get the list of stocks that exist:              # Completed 
    Check Database for the last day of data
        1. if no data exists run retrieval          # Completed 
        2. else check the latest date of the database cross check it to the last month of data read from ws files  # Working on right now 
            if it matches proceed with process 
            else run get upload of data or run with out 
    when the data checks out 
        1. create dashboard and output data"""

"""
 Option 1: Transaction-Based Book Cost Timeline (Most Accurate)
Store each buy/sell transaction in a DB table:

Date

Shares bought

Price

Total cost

Currency

Create a cumulative book cost table that tracks:

Book cost (avg price per share) over time

Cumulative shares held

When pulling daily stock price:

Join the stock price with the book cost as of that day

Then: Adj Close - Book Cost (on that date)

Benefit:
Perfectly tracks your performance as of that date, including:

Past performance before and after new buys

Changing positions

Partial sells
"""