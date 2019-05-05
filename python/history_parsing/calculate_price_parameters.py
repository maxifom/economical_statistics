"""
    Calculate price parameters (log return, overnight and trading day variations
"""


import pandas as pd
from models.models import *

if __name__ == '__main__':
    companies = Company.select()
    for c in companies:
        df = pd.read_csv(f"./../../data/prices/{c.ticker}.csv")
        df["last_closing_price"] = df["close"].shift(1)
        df["overnight_variation"] = df["close"] - df["last_closing_price"]
        df["overnight_variation"].fillna(0, inplace=True)
        df["trading_day_variation"] = df["high"] - df["low"]
        df["pct_change"] = df["close"].pct_change()
        df["log_return"] = pd.np.log(1 + df["pct_change"])
        df["log_return"].fillna(0, inplace=True)
        del df["last_closing_price"], df["pct_change"]
        df.to_csv(f"./../../data/prices/{c.ticker}.csv", index=False)
