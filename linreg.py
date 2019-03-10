import pickle
from datetime import datetime

import pytz

import analysis
import moex
from database import Database
from history import get_news_history

if __name__ == '__main__':

    news = get_news_history()
    linreg_params = list()
    db = Database()
    companies_dict = dict()
    companies = db.get_all_companies()
    for c in companies:
        companies_dict[c["id"]] = c["ticker"]
    _n = 0
    for n in news:
        if _n <= 2144:
            _n += 1
            continue
        lp = dict()
        info = analysis.sentence_info(n["text"])
        lp["sent_score"] = info["score"]
        lp["word_count"] = info["count"]
        tz = pytz.timezone("Europe/Moscow")
        time = tz.localize(datetime.fromtimestamp(n["timestamp"]))
        start_time = time.replace(hour=9, minute=58)
        end_time = time.replace(hour=19, minute=0)
        if time <= start_time or time >= end_time:
            _n += 1
            continue
        info = moex.getHistoryInfo(companies_dict[n["companies"].pop()], time)
        if info is None:
            _n += 1
            continue
        lp["log_return"] = info["log_return"]
        lp["trading_volume"] = info["trading_volume"]
        lp["overnight_variation"] = info["overnight_variation"]
        lp["trading_day_variation"] = info["trading_day_variation"]
        lp["next_price"] = info["next_price"]
        lp["closing_price"] = info["closing_price"]
        lp["news_id"] = _n
        _n += 1
        print(lp)
        print(_n, datetime.now())
        linreg_params.append(lp)
        if _n % 15 == 0 and n != 0:
            with open('linreg.pickle', 'ab') as lgfile:
                pickle.dump(linreg_params, lgfile)
    with open('linreg.pickle', 'ab') as lgfile:
        pickle.dump(linreg_params, lgfile)
    print(linreg_params)
