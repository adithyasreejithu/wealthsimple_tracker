"""
This file will gather information on the portofolio and add 
it to the database 

"""
import os 
import logging
import pandas as pd 
import yfinance as yf 
import db_func as func
from datetime import datetime, timedelta
from curl_cffi import requests

# Will need to create a central logging file when this is completed
logger = logging.getLogger("gather_stock_history") # Name of the logger 
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("file_processing.log", mode="w")
file_handler.setLevel(logging.DEBUG)

# Creating Formatter 
formatter = logging.Formatter(
    "%(levelname)s | %(name)s: %(message)s"
)

# Adding formatter and handler to logger
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# dataset = None

class YFinanceFetcher:
    def __init__(self, ticker):
        self.ticker = ticker
        self.sdate = os.getenv("PORTFOILIO_STARTDATE")
        self.tdy = datetime.today().strftime("%Y-%m-%d")
        self.hist = func.hist_database_check()
        self.bookcost = 0
        self.shares = 0 
        self.value = 0 

    def _get_stock_history_db(self):
        if self.hist == []: # In real usecase this will be !=
            # Call database look for last date 
            # Get the last information given
            pass

    def _get_ticker_suffix(self):
        # Append '.TO' if ticker is Canadian
        if self.ticker[1].lower() == "cad":
            return self.ticker[0] + ".TO"
        return self.ticker[0]

    def _modify_dataframe(self, dataset):
        func.get_stock_data_bundle(self.ticker)
        custom_hist = ["Open", "Close", "High", "Low", "Adj Close"]
        dataset = dataset[custom_hist].copy()
        dataset = dataset.reset_index()
        dataset["Date"] = pd.to_datetime(dataset["Date"]).dt.date
        return dataset
    
    def _reformat_dataframe_db(self, dataset):
        stock_id = func.pull_stock_id(self.ticker[0], None, None)
        dataset["Stock_ID"] = stock_id
        dataset["Date"] = pd.to_datetime(dataset["Date"]).dt.date

        dataset = dataset.rename(columns={
            "Adj Close": "Adj_close",
            "20D_Moving": "Moving_Avg_20D",
            "20D_Volatility": "Volatility_20D",
            "20D_Expo_Moving_Average": "Expo_Moving_Average_20D"
        })

        dataset = dataset[[ 
            "Date", "Stock_ID", "Open", "Close", "Adj_close", "High", "Low",
            "Book_Cost", "Shares", "Total_Value", "Unreal_Gains", "Daily_Change",
            "Moving_Avg_20D", "Volatility_20D", "Expo_Moving_Average_20D"
        ]]

        print(dataset.head())
        func.dateframe_to_db(dataset)
    
    def _populate_dataframe(self, dataset):
        bundle = func.get_stock_data_bundle(self.ticker)

        dataset["Date"] = pd.to_datetime(dataset["Date"])
        bundle.purchases["Executed_Date"] = pd.to_datetime(bundle.purchases["Executed_Date"])

        for i, date in enumerate(dataset["Date"]):

            if date in bundle.purchases["Executed_Date"].values:
                matched_data = bundle.purchases.loc[bundle.purchases["Executed_Date"] == date,["Fx_Rate", "Shares", "Value"]]

                if not matched_data.empty:
                    new_shares = matched_data["Shares"].iloc[0]
                    new_value = matched_data["Value"].iloc[0]

                    self.shares += new_shares
                    self.value += new_value
                    self.bookcost += self.value / self.shares if self.shares != 0 else 0

            adj_close = dataset.loc[i, "Adj Close"]
            dail_change = adj_close - self.bookcost if self.bookcost != 0 else 0

            dataset.loc[i, "Shares"] = self.shares
            dataset.loc[i, "Values"] = self.value
            dataset.loc[i, "Book_Cost"] = self.bookcost
            dataset.loc[i, "Daily_Change"] = dail_change
            dataset.loc[i, "Total_Value"] = adj_close*self.shares
            dataset.loc[i, "Unreal_Gains"] = (adj_close-self.bookcost)*self.shares
        
        dataset["20D_Moving"] = dataset["Adj Close"].rolling(window=20).mean()
        dataset["20D_Volatility"] = dataset["Adj Close"].rolling(window=20).std()/dataset["Adj Close"].rolling(window=20).mean()
        dataset["20D_Expo_Moving_Average"]= dataset["Adj Close"].ewm(span=20, adjust=False).mean()

        self._reformat_dataframe_db(dataset)
        
    def __call__(self):
        try:
            suffix = self._get_ticker_suffix()
            session = requests.Session(impersonate="chrome")
            stock = yf.Ticker(suffix, session=session)
            self.history = stock.history(start=self.sdate, end=self.tdy, interval="1d", auto_adjust=False)
            cleaned_data = self._modify_dataframe(self.history)
            self._populate_dataframe(cleaned_data)

            return cleaned_data
        except Exception as e:
            logger.debug(f"Exception occurred: {e}")
            return None
        

# if __name__ == "__main__":
#     main()

tickers = func.get_tickers()
# hist_data = func.hist_database_check()

# fetch = YFinanceFetcher(("PZA", "Cad")) 
# df = fetch()

for tick in tickers:    
    fetch = YFinanceFetcher(tick)
    df = fetch()

