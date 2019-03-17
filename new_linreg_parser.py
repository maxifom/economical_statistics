import math
import pickle
import random
from datetime import datetime, timedelta

import pytz
import requests
from lxml import objectify

import analysis
from database import Database


def get_price_for_timestamp(ticker, timestamp):
    tz = pytz.timezone("Europe/Moscow")
    till_time = tz.localize(datetime.fromtimestamp(timestamp))
    from_time = till_time
    fr = from_time.strftime("%Y-%m-%d")
    url = "http://iss.moex.com/iss/engines/stock/markets/shares/securities/" + ticker + "/candles?interval=60&from=" + fr + "&till=" + fr
    r = requests.get(url)
    root = objectify.fromstring(r.text.encode('utf-8'))
    rows = root.data.rows.getchildren()
    if len(rows) == 0:
        return -1
    if from_time < tz.localize(datetime.strptime(rows[0].attrib["begin"], "%Y-%m-%d %M:%H:%S")):
        return float(rows[0].attrib["close"])
    if from_time > tz.localize(datetime.strptime(rows[len(rows) - 1].attrib["begin"], "%Y-%m-%d %M:%H:%S")):
        return float(rows[len(rows) - 1].attrib["close"])
    for r in rows:
        if tz.localize(datetime.strptime(r.attrib["begin"], "%Y-%m-%d %M:%H:%S")) > from_time:
            return float(r.attrib["close"])
    return -1.0


def get_all_days_history(ticker):
    from_time = datetime(2017, 1, 1, 0, 0, 0)
    fr = from_time.strftime("%Y-%m-%d")
    url = "http://iss.moex.com/iss/engines/stock/markets/shares/securities/" + ticker + "/candles?interval=24&from=" + fr
    r = requests.get(url)
    root = objectify.fromstring(r.text.encode('utf-8'))
    rows = root.data.rows.getchildren()
    last_parsed_day = from_time
    while last_parsed_day < datetime.now() - timedelta(days=2):
        last_parsed_day = datetime.strptime(rows[len(rows) - 1].attrib["begin"], "%Y-%m-%d %M:%H:%S")
        fr = last_parsed_day.strftime("%Y-%m-%d")
        url = "http://iss.moex.com/iss/engines/stock/markets/shares/securities/" + ticker + "/candles?interval=24&from=" + fr
        r = requests.get(url)
        root = objectify.fromstring(r.text.encode('utf-8'))
        for r in root.data.rows.getchildren():
            rows.append(r)
    return rows


def get_prev_day_close(ticker, timestamp):
    tz = pytz.timezone("Europe/Moscow")
    till_time = tz.localize(datetime.fromtimestamp(timestamp))
    from_time = till_time - timedelta(days=10)
    till_time = till_time - timedelta(days=1)
    fr = from_time.strftime("%Y-%m-%d")
    tr = till_time.strftime("%Y-%m-%d")
    url = "http://iss.moex.com/iss/engines/stock/markets/shares/securities/" + ticker + "/candles?interval=24&from=" + fr + "&till=" + tr
    r = requests.get(url)
    root = objectify.fromstring(r.text.encode('utf-8'))
    rows = root.data.rows.getchildren()
    if len(rows) != 0:
        return float(rows[len(rows) - 1].attrib["close"])
    return -1


from multiprocessing.dummy import Pool as ThreadPool

pool = ThreadPool(16)


def processNews(n):
    n["company_id"] = n["companies"].pop()
    n["info"] = analysis.sentence_info(n["text"])
    del n["companies"]
    n["log_return"] = 0
    close = get_prev_day_close(companies_dict[n["company_id"]], n["timestamp"])
    price = get_price_for_timestamp(companies_dict[n["company_id"]], n["timestamp"])
    if close > 0 and price > 0:
        n["log_return"] = math.log(price) - math.log(close)
    print(n)
    r1 = random.randint(1, 100)
    with open('./xml/' + str(r1) + str(n["timestamp"]), 'wb') as file:
        pickle.dump(n, file)


if __name__ == '__main__':
    # # get_all_days_history("YNDX")
    db = Database()
    companies_dict = dict()
    companies = db.get_all_companies()
    for c in companies:
        companies_dict[c["id"]] = c["ticker"]

    # # news = history.get_news_history()
    # # print(len(news))
    # # i = 0
    # # news_result = pool.map(processNews, news)
    # # # for n in news:
    # # #     processNews(n)
    # # # if i % 100 == 0 and i != 0:
    # # #     with open('news_with_sentence_info', 'wb') as fp:
    # # #         pickle.dump(news, fp)
    # # pool.close()
    # # pool.join()
    # # with open('news_with_sentence_info', 'wb') as fp:
    # #     pickle.dump(news, fp)
    #
    # with open('news_with_sentence_info', 'rb') as fp:
    #     news = pickle.load(fp)
    #
    # for _, c in companies_dict.items():
    #     print(c)
    # news.sort(key=lambda n: n["timestamp"])
    # i = 0
    # for n in news:
    #     db.db.execute("""
    #         INSERT INTO news(company_id,link,body,word_count,sent_score, log_return, time)
    #         VALUES (%s,%s,%s,%s,%s,%s, FROM_UNIXTIME(%s))
    #     """, (
    #         n["company_id"], n["url"], n["text"], n["info"]["count"], n["info"]["score"],
    #         n["log_return"], n["timestamp"]))
    #     db.connection.commit()
    #     i += 1
    #     print(i)
    # lin_reg_params = list()
    # for id, ticker in companies_dict.items():
    #     rows = get_all_days_history(ticker)
    #     for i in range(1, len(rows) - 1):
    #         lp = dict()
    #         db.db.execute("""
    #                     SELECT SUM(word_count) as count,AVG(sent_score) as sent_score, AVG(log_return) as log_return FROM news WHERE company_id=%s AND time >%s AND time <%s GROUP BY company_id
    #                 """, (id, rows[i].attrib["begin"], rows[i].attrib["end"]))
    #         aggr = db.db.fetchone()
    #         lp["sent_score"] = 0.0
    #         lp["word_count"] = 0
    #         lp["log_return"] = 0
    #         if aggr is not None:
    #             lp["sent_score"] = float(aggr["sent_score"])
    #             lp["log_return"] = float(aggr["log_return"])
    #             lp["word_count"] = int(aggr["count"])
    #         lp["trading_volume"] = float(rows[i].attrib["value"])
    #         lp["trading_day_variation"] = float(rows[i].attrib["high"]) - float(rows[i].attrib["low"])
    #         lp["overnight_variation"] = float(rows[i].attrib["open"]) - float(rows[i - 1].attrib["close"])
    #         lp["closing_price"] = float(rows[i].attrib["close"])
    #         lp["next_closing_price"] = float(rows[i + 1].attrib["close"])
    #         lin_reg_params.append(lp)
    #     print(id)
    # print(lin_reg_params)
    # with open("linreg_params", 'wb') as fp:
    #     pickle.dump(lin_reg_params, fp)
    # print(len(lin_reg_params))
    # print(lin_reg_params)
    with open("linreg_params", 'rb') as fp:
        lin_reg_params = pickle.load(fp)
    ld = list()
    for l in lin_reg_params:
        # if l["sent_score"] != 0 and l["log_return"] != 0:
        ld.append(l)
    print(ld)
    print(len(ld))
    with open("linreg_params_flat", 'wb') as wb:
        pickle.dump(ld, wb)
    # with open("linreg_params_flat", 'rb') as rb:
    #     lg = pickle.load(rb)

    headers = ['sent_score', 'log_return', 'trading_volume', 'overnight_variation',
               'trading_day_variation', 'word_count', 'closing_price', 'next_closing_price']
    import csv

    with open('ligreg1.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(headers)
        for l in ld:
            item = []
            for h in headers:
                item.append(l[h])
            writer.writerow(item)
    import statsmodels.api as sm
    import pandas as pd

    df = pd.read_csv("ligreg1.csv")
    x = df.iloc[:, :-1]
    y = df.iloc[:, -1]
    import statsmodels.api as sm

    x_ = sm.add_constant(x)
    smm = sm.OLS(y, x_)
    res = smm.fit()
    print(res.params)
    for r in res.params:
        print("{:10.15f}".format(r))
