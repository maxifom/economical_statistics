import math

import numpy
import pandas as pd
from datetime import datetime as date
import pytz

if __name__ == '__main__':
    tickers = ["SFIN", "FIVE", "ALRS", "AFLT", "VTBR", "GAZP", "PIKK", "DSKY", "IRAO", "LKOH", "MVID", "MGNT", "MFON",
               "MTLR", "CBOM", "MAGN", "MOEX", "MTSS", "NLMK", "NMTP", "NVTK", "GMKN", "UWGN", "POLY", "PLZL", "AGRO",
               "ROSN", "RSTI", "RTKM", "RUAL", "HYDR", "RNFT", "SBER", "CHMF", "AFKS", "SNGS",  "TATN",
                "TRMK", "TRNFP", "PHOR", "FEES", "UPRO", "YNDX"]
    all_news = pd.read_csv('./csv/news_with_one_company.csv')
    tz = pytz.timezone("Europe/Moscow")
    for t in tickers:
        minutely_history = pd.read_csv('./csv/history_{0}_1.csv'.format(t))
        daily_history = pd.read_csv('./csv/history_{0}_24.csv'.format(t))
        daily_history_dict = daily_history.to_dict(orient='rows')
        prev_close = 0
        index = 0
        for d in daily_history_dict:
            if not isinstance(d["time"], str):
                continue
            time = date.strptime(d["time"], "%Y-%m-%d %H:%M:%S%z").astimezone(tz)
            start_time = time.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = time.replace(hour=23, minute=59, second=59, microsecond=999999)
            d["trading_day_variation"] = float(d["high"]) - float(d["low"])
            if prev_close == 0:
                d["overnight_variation"] = 0
            else:
                d["overnight_variation"] = float(d["open"]) - float(prev_close)
            daily_news = all_news[(all_news["companies"] == t) & (start_time.timestamp() <= all_news["timestamp"]) & (
                    all_news["timestamp"] <= end_time.timestamp())]
            d["sent_score"] = daily_news['sent_score'].mean()
            if numpy.isnan(d["sent_score"]):
                d["sent_score"] = 0
            d["word_count"] = daily_news["word_count"].sum()
            if numpy.isnan(d["word_count"]):
                d["word_count"] = 0
            d["log_return"] = math.log(d["close"]) - math.log(d["open"])
            d["next_closing_price"] = daily_history_dict[index + 1]["close"]
            prev_close = float(d["close"])
            index += 1
        new_df = pd.DataFrame.from_dict(daily_history_dict).reset_index(drop=True)
        new_df.to_csv('./csv/parsed_{0}.csv'.format(t),
                      columns=['sent_score', 'log_return', 'volume', 'overnight_variation',
                               'trading_day_variation', 'word_count', 'close',
                               'next_closing_price', 'time'])
