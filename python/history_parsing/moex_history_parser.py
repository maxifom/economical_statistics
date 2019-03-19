import datetime
from multiprocessing.dummy import Pool as ThreadPool

import numpy as np
import pandas as pd

import pytz
import requests
from lxml import objectify


class MoexHistoryParser:
    def __init__(self, start_date=datetime.datetime.now(), end_date=datetime.datetime.now(), interval=1, ticker='YNDX'):
        tz = pytz.timezone("Europe/Moscow")
        if start_date.tzinfo is None:
            start_date = tz.localize(start_date)
        if end_date.tzinfo is None:
            end_date = tz.localize(end_date)
        self.start_date = start_date.strftime("%Y-%m-%d")
        self.end_date = end_date.strftime("%Y-%m-%d")
        self.interval = interval
        self.ticker = ticker
        self.parse_url = "http://iss.moex.com/iss/engines/stock/markets/shares/securities/{0}/candles?interval={1}&from={2}&till={3}&start={4}"
        self.history = pd.DataFrame(index=['time'], columns=['open', 'high', 'low', 'close', 'volume', 'trade_count'])

    def get_all_count(self):
        if self.interval == 1:
            start = prev_start = 210000
        elif self.interval == 24:
            start = prev_start = 0
        result_count = 500
        while result_count == 500:
            r = requests.get(self.parse_url.format(self.ticker, self.interval, self.start_date, self.end_date, start))
            root = objectify.fromstring(r.text.encode('utf-8'))
            rows = root.data.rows.getchildren()
            result_count = len(rows)
            if start == prev_start and result_count != 500 and self.interval == 1:
                start -= 5000
                prev_start -= 5000
                result_count = 500
            else:
                start += result_count
        print(str(self.ticker) + " count:" + str(start))
        return start

    def parse(self, num_of_threads=8):
        count = self.get_all_count()
        list_to_parse = np.arange(0, count, 500).tolist()
        pool = ThreadPool(num_of_threads)
        pool.map(self.parse_one_entry, list_to_parse)
        pool.close()
        pool.join()

    def parse_one_entry(self, start):
        tz = pytz.timezone("Europe/Moscow")
        r = requests.get(self.parse_url.format(self.ticker, self.interval, self.start_date, self.end_date, start))
        root = objectify.fromstring(r.text.encode('utf-8'))
        rows = root.data.rows.getchildren()
        row_list = list()
        for r in rows:
            item = dict()
            item['time'] = pd.to_datetime(tz.localize(
                datetime.datetime.strptime(r.attrib['begin'], "%Y-%m-%d %H:%M:%S")).astimezone(pytz.utc))
            item['open'] = r.attrib['open']
            item['high'] = r.attrib['high']
            item['low'] = r.attrib['low']
            item['close'] = r.attrib['close']
            item['volume'] = r.attrib['value']
            item['trade_count'] = r.attrib['volume']
            row_list.append(item)
        i = pd.DataFrame(row_list)
        self.history = pd.concat([self.history, i], sort=True, ignore_index=True)

    def save_to_file(self, file):
        self.history.sort_values(by='time', ascending=True, inplace=True)
        self.history.to_csv(file)


def parse_daily_history():
    for t in tickers:
        print(t)
        now = datetime.datetime.now()
        interval = 24
        parser = MoexHistoryParser(start_date=datetime.datetime(2017, 1, 1, 0, 0, 0), ticker=t, interval=interval)
        parser.parse(num_of_threads=1)
        parser.save_to_file('./csv/history_' + t + '_' + str(interval) + '.csv')
        print(datetime.datetime.now() - now)


def process_ticker(t):
    print(t)
    now = datetime.datetime.now()
    interval = 1
    parser = MoexHistoryParser(start_date=datetime.datetime(2017, 1, 1, 0, 0, 0), ticker=t, interval=interval)
    parser.parse(num_of_threads=4)
    parser.save_to_file('./csv/history_' + t + '_' + str(interval) + '.csv')
    print("Parsing " + t + " took " + str(datetime.datetime.now() - now))


def parse_minute_history(num_of_threads=8):
    pool = ThreadPool(num_of_threads)
    pool.map(process_ticker, tickers)
    pool.close()
    pool.join()


if __name__ == '__main__':
    tickers = ["SFIN", "FIVE", "ALRS", "AFLT", "VTBR", "GAZP", "PIKK", "DSKY", "IRAO", "LKOH", "MVID", "MGNT", "MFON",
               "MTLR", "CBOM", "MAGN", "MOEX", "MTSS", "NLMK", "NMTP", "NVTK", "GMKN", "UWGN", "POLY", "PLZL", "AGRO",
               "ROSN", "RSTI", "RTKM", "RUAL", "HYDR", "RNFT", "SBER", "SBERP", "CHMF", "AFKS", "SNGS", "SNGSP", "TATN",
               "TATNP", "TRMK", "TRNFP", "PHOR", "FEES", "UPRO", "YNDX"]
    parse_daily_history()
    parse_minute_history()
