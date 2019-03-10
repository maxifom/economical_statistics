import math
from datetime import datetime, timedelta

import pytz
import requests
from lxml import objectify


def getHistoryInfo(ticker, time):
    tz = pytz.timezone("Europe/Moscow")
    # till_time = tz.localize(datetime(2017, 1, 4, 10, 5, 0, 0))
    if time.tzinfo is None:
        till_time = tz.localize(time)
    else:
        till_time = time
    prev_day = till_time - timedelta(days=1)
    from_time = tz.localize(datetime(2017, prev_day.month, prev_day.day, 9, 0, 0))
    fr = from_time.strftime("%Y-%m-%d")
    till = till_time.strftime("%Y-%m-%d")
    url = "http://iss.moex.com/iss/engines/stock/markets/shares/securities/" + ticker + "/candles?interval=1&from=" + fr + "&till=" + fr + "&start=350"
    # print(url)
    r = requests.get(url)
    root = objectify.fromstring(r.text.encode('utf-8'))
    rows = root.data.rows.getchildren()
    if len(rows) == 0:
        return None
    last_day_close = rows[len(rows) - 1].attrib["close"]
    # print(last_day_close)
    url = "http://iss.moex.com/iss/engines/stock/markets/shares/securities/" + ticker + "/candles?interval=1&from=" + till + "&till=" + till
    # print(url)
    r = requests.get(url)
    root = objectify.fromstring(r.text.encode('utf-8'))
    rows = root.data.rows.getchildren()
    this_day_open = rows[0].attrib["open"]
    # prev_row = rows[0]
    # last_day_close = prev_close = this_day_open = 0
    # is_this_day = False
    _open = close = 0
    index = 0
    maximum = minimum = 0
    breaked = False
    for row in rows:
        date = tz.localize(datetime.strptime(row.attrib['begin'], "%Y-%m-%d %H:%M:%S"))
        if date > till_time:
            breaked = True
            break
        high = row.attrib["high"]
        low = row.attrib["low"]
        _open = row.attrib['open']
        close = row.attrib['close']
        # if not (date.day == from_time.day and date.month == from_time.month) and not is_this_day:
        #     last_day_close = prev_row.attrib["close"]
        #     this_day_open = _open
        #     maximum = float(prev_row.attrib["high"])
        #     minimum = float(prev_row.attrib["low"])
        #     is_this_day = True
        # prev_row = row
        # if is_this_day:
        maximum = max(maximum, float(high))
        minimum = min(minimum, float(low))
        index += 1
    if not breaked:
        print('Not breaked')
        url = "http://iss.moex.com/iss/engines/stock/markets/shares/securities/" + ticker + "/candles?interval=1&from=" + till + "&till=" + till + "&start=499"
        # print(url)
        r = requests.get(url)
        root = objectify.fromstring(r.text.encode('utf-8'))
        rows = root.data.rows.getchildren()
        index = 0
        for row in rows:
            date = tz.localize(datetime.strptime(row.attrib['begin'], "%Y-%m-%d %H:%M:%S"))
            if date > till_time:
                break
            high = row.attrib["high"]
            low = row.attrib["low"]
            _open = row.attrib['open']
            close = row.attrib['close']
            maximum = max(maximum, float(high))
            minimum = min(minimum, float(low))
            index += 1
    delta = timedelta(minutes=5)
    prev_volume = 0
    next_closing_price = -1
    prev_closing_price = -1
    if index == 0:
        prev_closing_price = last_day_close
    else:
        for i in range(index - 2, index - 12, -1):
            if len(rows) > i >= 0:
                prev_closing_price = rows[i].attrib["close"]
                if (till_time - tz.localize(datetime.strptime(rows[i].attrib['begin'], "%Y-%m-%d %H:%M:%S"))) >= delta:
                    prev_volume = rows[i].attrib["value"]
                    break
    # print(index)
    # print(len(rows))
    # print(till_time)
    # print(ticker)
    for i in range(index - 1, index + 10):
        if len(rows) > i >= 0:
            next_closing_price = float(rows[i].attrib["close"])
            if (tz.localize(
                    datetime.strptime(rows[i].attrib['begin'], "%Y-%m-%d %H:%M:%S")) - till_time) >= delta:
                # print(rows[i].attrib["begin"])
                break

    result = dict()
    if float(prev_closing_price) < 0:
        result["log_return"] = -1
    else:
        result["log_return"] = math.log(float(close)) - math.log(float(prev_closing_price))
    result["overnight_variation"] = float(this_day_open) - float(last_day_close)
    result["trading_volume"] = float(prev_volume)
    result["closing_price"] = float(close)
    result["trading_day_variation"] = maximum - minimum
    result["next_price"] = next_closing_price
    return result


if __name__ == '__main__':
    # print(getHistoryInfo("YNDX", datetime(2017, 1, 4, 10, 0, 0, 0)))
    print(getHistoryInfo("LKOH", datetime(2017, 1, 12, 13, 8, 0, 0)))
