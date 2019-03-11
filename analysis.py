coef_1 = -0.95726304
coef_2 = -0.23373012
coef_3 = -87.81500699
coef_4 = 0.00000009
coef_5 = 0.00783021
coef_6 = 0.09414829
coef_7 = -0.00101384
coef_8 = 0.90555433

import math
import re

import pymorphy2
import requests
import scrapy
from polyglot.text import Text

from database import Database

morpher = pymorphy2.MorphAnalyzer()


def sentence_info(sentence):
    sentence = sentence.replace('.', ' ').replace(',', ' ').replace('\n', '').replace('\t', '').lstrip(' ').rstrip(
        ' ').replace('"', '').replace('  ', ' ')
    sentence = sentence.split(' ')
    for i in range(len(sentence)):
        sentence[i] = morpher.parse(sentence[i])[0].normal_form
    sentence = ' '.join(sentence)
    text = Text(text=sentence, hint_language_code='ru')
    word_count = 0
    for key, c in text.word_counts.items():
        word_count += c
    result = dict()
    result['score'] = text.polarity
    result['count'] = word_count
    return result


def get_news_company_id(news):
    only_news = list()
    db = Database()
    db.db.execute("SELECT id,parse_name FROM companies")
    names = db.db.fetchall()
    names_to_search = dict()
    for n in names:
        names_to_search[n["id"]] = dict()
        names_to_search[n["id"]]["names"] = n["parse_name"].split(", ")
    for n in news:
        n["companies"] = set()
        found = re.findall(r'\"[A-ZА-Я][a-zA-Zа-яА-Я\s\-.,]*\"', n["text"])
        for f in found:
            for q, w in names_to_search.items():
                for name in w["names"]:
                    if name in f:
                        n["companies"].add(q)  # company id
                        break
        if len(n["companies"]) == 1:
            only_news.append(n)
    return only_news


def get_overnight_variation(company_id):
    db = Database()
    db.db.execute("""
            SELECT url from companies WHERE id = %s LIMIT 1
        """, (company_id,))
    url = db.db.fetchone()['url']
    print(url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 YaBrowser/19.3.0.2485 Yowser/2.5 Safari/537.36'
    }
    body = requests.get(url, headers=headers)
    sel = scrapy.selector.Selector(response=body)
    prev_close = float(sel.xpath(
        '//div[@class="clear overviewDataTable overviewDataTableWithTooltip"][1]/div[1]/span[2]/text()').extract_first().replace(
        ',', '.'))
    this_day_open = float(sel.xpath(
        '//div[@class="clear overviewDataTable overviewDataTableWithTooltip"][1]/div[4]/span[2]/text()').extract_first().replace(
        ',', '.'))
    return this_day_open - prev_close


def get_price_info(n):
    db = Database()
    company_id = str([n["companies"].copy().pop()][0])
    db.db.execute("""
        SELECT id,current, volume, volume_previous,high,low FROM prices WHERE company_id = %s AND UNIX_TIMESTAMP(time) <= %s ORDER BY id DESC LIMIT 2
    """, (company_id, n["timestamp"]))  # Get 2 last prices (closing price + prev for logreturn and trading_volume
    last_two = db.db.fetchall()
    if len(last_two) < 2:
        db.db.execute("""
            DELETE FROM news WHERE link=%s
        """, (n["url"],))
        db.connection.commit()
        return None
    trading_volume = last_two[0]["volume_previous"]
    log_return = math.log(last_two[0]["current"]) - math.log(last_two[1]["current"])
    trading_day_variation = last_two[0]["high"] - last_two[0]["low"]
    overnight_variation = get_overnight_variation(company_id)
    closing_price = last_two[0]["current"]
    info = {
        "trading_volume": trading_volume,
        "log_return": log_return,
        "trading_day_variation": float(trading_day_variation),
        "overnight_variation": overnight_variation,
        "closing_price": float(closing_price)
    }
    return info


companies_dict = dict()


def calculate_predictions(news_to_update):
    db = Database()
    companies = db.get_all_companies()
    for c in companies:
        companies_dict[c["id"]] = c["ticker"]
    for n in news_to_update:
        n["price_info"] = get_price_info(n)
        p = n["price_info"]
        if p is not None:
            prediction = coef_1 + coef_2 * n["info"]["score"] + coef_3 * p["log_return"] + coef_4 * p[
                "trading_volume"] + coef_5 * p["overnight_variation"] + coef_6 * p["trading_day_variation"] + coef_7 * \
                         n["info"]["count"] + coef_8 * p["closing_price"]

            db.db.execute("""
                   UPDATE news SET prediction = %s,trading_volume = %s, log_return = %s, trading_day_variation=%s,overnight_variation=%s,closing_price=%s WHERE link=%s 
                """, (prediction,
                      p["trading_volume"], p["log_return"], p["trading_day_variation"], p["overnight_variation"],
                      p["closing_price"],
                      n["url"]))
            db.connection.commit()
