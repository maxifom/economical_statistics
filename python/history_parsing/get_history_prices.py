"""
    Get daily candle price data for each company
"""

import time

import requests
import pandas as pd
import io

from models.models import *

if __name__ == '__main__':
    companies = Company.select()
    for c in companies:
        ticker = c.ticker
        url = f"http://export.finam.ru/{ticker}.csv?market=1&em={c.finam_id}&code={ticker}&apply=0&df=7&mf=4&yf=1981&from=07.05.1981&dt=1&mt=4&yt=2019&to=01.05.2019&p=8&f={ticker}&e=.csv&cn={ticker}&dtf=1&tmf=1&MSOR=1&mstimever=0&sep=1&sep2=1&datf=1&at=1&fsp=1"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/73.0.3683.86 YaBrowser/19.4.0.2397 Yowser/2.5 Safari/537.36',
        }
        response = requests.get(url, headers=headers)
        df = pd.read_csv(io.StringIO(response.content.decode('utf-8')))
        df.rename(columns={"<DATE>": "date", "<TIME>": "time", "<OPEN>": "open", "<HIGH>": "high", "<LOW>": "low",
                           "<CLOSE>": "close",
                           "<VOL>": "volume"}, inplace=True)
        del df["time"]
        del df["<TICKER>"]
        del df["<PER>"]
        df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
        df.to_csv(f"./../../data/prices/{ticker}.csv", index=False)
        time.sleep(2)
