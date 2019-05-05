"""
    Calculates parameters for prediction (last 30 days) and predicts the next day closing price
"""


import decimal
import json
from models import *

from datetime import datetime, timedelta

import math
import pandas as pd


def predict():
    companies = Company.select()
    for c in companies:
        p = Prediction()
        overnight_query = Price.select(fn.MAX(Price.high - Price.low).alias('over')).where(
            (Price.company == c.id) & (Price.time >= datetime.utcnow() - timedelta(days=30))).group_by(
            fn.MONTH(Price.time), fn.DAY(Price.time))
        over = SQL('over')
        p.mean_trading_day_variation = Price.select(fn.AVG(over).alias("mtdv")).from_(overnight_query).get().mtdv

        sentiment_query = News.select(fn.AVG(News.sent_score).alias("ss"), fn.AVG(News.word_count).alias("wc")).where(
            (News.company == c.id) & (News.time >= datetime.utcnow() - timedelta(days=30))).get()
        p.mean_sent_score, p.mean_word_count = sentiment_query.ss or 0, sentiment_query.wc or 0

        volume_query = Price.select(fn.MAX(Price.volume).alias('vol')).where(
            (Price.company == c.id) & (Price.time >= datetime.utcnow() - timedelta(days=30))).group_by(
            fn.MONTH(Price.time), fn.DAY(Price.time))
        vol = SQL("vol")
        p.mean_trading_volume = Price.select(fn.AVG(vol).alias("mtv")).from_(volume_query).get().mtv

        prices = Price.select(Price.current, Price.time).where(
            (Price.company == c.id) & (Price.time >= datetime.utcnow() - timedelta(days=30))).dicts()
        df = pd.DataFrame.from_dict(prices)
        close_prices = df.groupby(df.time.dt.date).current.last().reset_index()
        open_prices = df.groupby(df.time.dt.date).current.first().reset_index()
        overnight_variations = [0]
        for i in range(1, len(open_prices)):
            overnight_variations.append(float(open_prices.iloc[i].current - close_prices.iloc[i - 1].current))
        p.mean_overnight_variation = sum(overnight_variations) / len(overnight_variations)
        log_returns = [{"time": close_prices.iloc[0].time, "log_return": 0}]

        for i in range(1, len(close_prices)):
            l = dict()
            l["time"] = close_prices.iloc[i].time
            l["log_return"] = math.log(close_prices.iloc[i].current) - math.log(close_prices.iloc[i - 1].current)
            log_returns.append(l)

        ldf = pd.DataFrame(log_returns).set_index("time")
        date_range = pd.date_range(close_prices.iloc[0].time, close_prices.iloc[-1].time)
        ldf = ldf.reindex(date_range)
        ldf.interpolate(inplace=True)
        p.mean_log_return = ldf.log_return.mean()

        close_prices = close_prices.set_index("time")
        close_prices = close_prices.reindex(date_range)
        close_prices['log_return'] = ldf.log_return
        for i in range(len(close_prices)):
            if pd.isnull(close_prices.iloc[i].current):
                close_prices.loc[[close_prices.iloc[i].name], ['current']] = decimal.Decimal(math.exp(
                    close_prices.iloc[i].log_return + math.log(close_prices.iloc[i - 1].current))).quantize(
                    decimal.Decimal("100.00"))
        p.mean_closing_price = float(close_prices.current.mean())
        cf = json.loads(c.linear_model)["params"]
        p.prediction = cf["const"] + cf["trading_day_variation"] * float(p.mean_trading_day_variation) + cf[
            "sent_score"] * float(p.mean_sent_score) + cf["word_count"] * float(p.mean_word_count) + cf[
                           "volume"] * float(p.mean_trading_volume) + cf["overnight_variation"] * float(
            p.mean_overnight_variation) + \
                       cf["log_return"] * float(p.mean_log_return) + cf["close"] * float(p.mean_closing_price)

        results = Prediction.select(Prediction.id, Prediction.prediction).where(Prediction.company == c.id).order_by(
            Prediction.id.desc()).limit(1)
        last_prediction = results[0] if len(results) > 0 else None
        p.current = Price.select(Price.current).where(Price.company == c.id).order_by(Price.id.desc()).limit(
            1).get().current
        if last_prediction is None or round(
                float(last_prediction.prediction), 10) - round(float(p.prediction), 10) > 0:
            p.company = c.id
            p.save()
        elif last_prediction is not None:
            last_prediction.updated_at = datetime.utcnow()
            if p.current is not None:
                last_prediction.current = p.current
            last_prediction.save()


if __name__ == '__main__':
    predict()
