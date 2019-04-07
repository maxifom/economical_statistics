import decimal
import pickle

import math
from database import Database
import pandas as pd


def predict():
    with open("../data/companies.pickle", 'rb') as f:
        companies_info = pickle.load(f)
    db = Database()
    db.db.execute("""SELECT * FROM companies WHERE name NOT LIKE '%(прив.)%'""")
    companies = db.db.fetchall()
    for c in companies:
        coefs = list(filter(lambda p: p["ticker"] == c["ticker"], companies_info))[0]
        company_id = c["id"]
        db.db.execute("""
        SELECT AVG(over) as mean_trading_day_variation FROM (SELECT MAX(high-low) as over FROM prices WHERE company_id=%s AND time >= DATE_SUB(CURRENT_DATE,INTERVAL 30 DAY) GROUP BY MONTH(time), DAY(time)) as a
        """, (company_id,))
        mean_trading_day_variation = db.db.fetchone()["mean_trading_day_variation"]
        db.db.execute(
            """SELECT AVG(sent_score) as ss, AVG(word_count) as wc FROM news WHERE company_id=%s AND time>=DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY)""",
            (company_id,))
        row = db.db.fetchone()
        mean_sent_score, mean_word_count = row["ss"], row["wc"]
        if mean_sent_score is None:
            mean_sent_score = 0
        if mean_word_count is None:
            mean_word_count = 0
        db.db.execute(
            """SELECT AVG(vol) as mean_trading_volume FROM (SELECT MAX(volume) as vol FROM prices WHERE company_id=%s AND time>=DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY) GROUP BY MONTH(time), DAY(time)) as a""",
            (company_id,))
        mean_trading_volume = db.db.fetchone()["mean_trading_volume"]

        db.db.execute("""
            SELECT current, time FROM prices WHERE company_id=%s AND time>=DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY)
        """, (company_id,))
        prices = db.db.fetchall()
        df = pd.DataFrame.from_dict(prices)
        # print(df)
        close_prices = df.groupby(df.time.dt.date).current.last().reset_index()
        # print(close_prices)
        open_prices = df.groupby(df.time.dt.date).current.first().reset_index()
        # print(open_prices)
        overnight_variations = [0]
        for i in range(1, len(open_prices)):
            overnight_variations.append(float(open_prices.iloc[i].current - close_prices.iloc[i - 1].current))
        # print(overnight_variations)
        mean_overnight_variation = sum(overnight_variations) / len(overnight_variations)
        # print(mean_overnight_variation)
        log_returns = [{"time": close_prices.iloc[0].time, "log_return": 0}]

        for i in range(1, len(close_prices)):
            l = dict()
            l["time"] = close_prices.iloc[i].time
            l["log_return"] = math.log(close_prices.iloc[i].current) - math.log(close_prices.iloc[i - 1].current)
            log_returns.append(l)
        # print(log_returns)
        # print(mean_log_returns)

        ldf = pd.DataFrame(log_returns).set_index("time")
        date_range = pd.date_range(close_prices.iloc[0].time, close_prices.iloc[-1].time)
        ldf = ldf.reindex(date_range)
        ldf.interpolate(inplace=True)
        mean_log_return = ldf.log_return.mean()

        close_prices = close_prices.set_index("time")
        close_prices = close_prices.reindex(date_range)
        close_prices['log_return'] = ldf.log_return
        for i in range(len(close_prices)):
            if pd.isnull(close_prices.iloc[i].current):
                close_prices.loc[[close_prices.iloc[i].name], ['current']] = decimal.Decimal(math.exp(
                    close_prices.iloc[i].log_return + math.log(close_prices.iloc[i - 1].current))).quantize(
                    decimal.Decimal("100.00"))
        mean_closing_price = float(close_prices.current.mean())
        c = coefs["coef"]
        prediction = c["trading_day_variation"] * float(mean_trading_day_variation) + c[
            "sent_score"] * float(mean_sent_score) + c["word_count"] * float(mean_word_count) + c[
                         "volume"] * float(mean_trading_volume) + c["overnight_variation"] * float(
            mean_overnight_variation) + \
                     c["log_return"] * float(mean_log_return) + c["close"] * float(mean_closing_price)

        # print("%-50s %f" % ("Mean Trading Day Variation:", mean_trading_day_variation))
        # print("%-50s %f" % ("Mean Sentiment Score:", mean_sent_score))
        # print("%-50s %f" % ("Mean Word Count:", mean_word_count))
        # print("%-50s %f" % ("Mean Trading Volume:", mean_trading_volume))
        # print("%-50s %f" % ("Mean Overnight Variaton:", mean_overnight_variation))
        # print("%-50s %f" % ("Mean Log return:", mean_log_return))
        # print("%-50s %f" % ("Mean Closing prices:", mean_closing_price))
        # print("%-50s %f" % ("Prediction:", prediction))

        db.db.execute("""
            SELECT id, prediction FROM predictions WHERE company_id = %s ORDER BY id DESC LIMIT 1
        """, (company_id,))
        _last = db.db.fetchone()
        if _last is not None and "prediction" in _last:
            last_prediction, last_id = _last["prediction"], _last["id"]
        else:
            last_prediction = 0
        db.db.execute("""
                        SELECT current FROM prices WHERE company_id = %s ORDER BY id DESC LIMIT 1
                    """, (company_id,))
        current_price = db.db.fetchone()["current"]
        if round(float(last_prediction), 10) - round(float(prediction), 10):
            db.db.execute("""
               INSERT INTO predictions(company_id, mean_trading_day_variation, mean_sent_score, mean_word_count, mean_trading_volume, mean_overnight_variation, mean_log_return, mean_closing_price, prediction, actual, current) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,0, %s)
            """, (company_id,
                  mean_trading_day_variation, mean_sent_score, mean_word_count, mean_trading_volume,
                  mean_overnight_variation,
                  mean_log_return, mean_closing_price, prediction, current_price))
            db.connection.commit()
        else:
            db.db.execute("""
                UPDATE predictions SET updated_at = CURRENT_TIMESTAMP, current = %s WHERE id = %s
            """, (current_price, last_id))
            db.connection.commit()
        # dr = pd.date_range(close_prices.iloc[0].time, close_prices.iloc[-1].time)
        # print(dr)
        # dr.add(log_returns)


if __name__ == '__main__':
    predict()
# Mean Trading Day Variation 30 days
# SELECT AVG(over) as mean_trading_day_variation FROM (SELECT MAX(high-low) as over FROM prices WHERE company_id=1 AND time >= DATE_SUB(CURRENT_DATE,INTERVAL 30 DAY) GROUP BY MONTH(time), DAY(time)) as a
# Mean Sent score and word count 30 days
# SELECT AVG(sent_score), AVG(word_count) FROM news WHERE company_id=4 AND time>=DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY)
# Mean Trading volume 30 days
# SELECT AVG(vol) as mean_trading_volume FROM (SELECT MAX(volume) as vol FROM prices WHERE company_id=2 AND time>=DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY) GROUP BY MONTH(time), DAY(time)) as a
