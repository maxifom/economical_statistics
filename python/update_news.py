import os
from polyglot.text import Text

from database import Database
import pytz
import scrapy
from scrapy.crawler import CrawlerProcess
import logging
from datetime import datetime

news = list()


def get_news():
    logging.getLogger('scrapy').propagate = False
    spider = FinamNewsSpider()
    news_parsing_process = CrawlerProcess()
    news_parsing_process.crawl(spider)
    news_parsing_process.start()
    return news


class FinamNewsSpider(scrapy.Spider):
    name = "finam_news_spider"

    def start_requests(self):
        urls = ["https://www.finam.ru/analysis/conews/"]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        news = response.xpath('//*[@id="content-block"]/table[2]/tr')
        urls = []
        for n in news:
            urls.append('https://finam.ru' + n.xpath('.//a[@class="f-fake-url"]/@href').extract_first())
        for url in urls:
            yield response.follow(url=url, callback=self.parse_news)

    def parse_news(self, response):
        title = response.xpath('//div[@id="news-item"]//h1[1]/text()').extract_first()
        body = response.xpath('//*[contains(@class,"f-newsitem-text")][1]/p//text()').extract()
        body_str = ''
        for text in body:
            body_str += text.replace('\xa0', ' ')
        time = response.xpath('//*[@class="sm lightgrey mb20 mt15"][1]/text()').extract_first().rstrip('\xa0')
        tz = pytz.timezone("Europe/Moscow")
        timestamp = int(tz.localize(datetime.strptime(time, "%d.%m.%Y %H:%M"), is_dst=0).timestamp())
        n = dict()
        n["text"] = title + '. ' + body_str
        n["url"] = response.url
        n["timestamp"] = timestamp
        news.append(n)


def update_counter(current_timestamp):
    current_timestamp = int(current_timestamp)
    if not os.path.exists("./news_timestamp"):
        with open("./news_timestamp", 'w') as news_count:
            news_count.write(str(current_timestamp))
            return -1
    else:
        with open("./news_timestamp", 'r+') as news_count:
            last_timestamp = int(news_count.read())
            if last_timestamp != current_timestamp:
                news_count.seek(0)
                news_count.write(str(current_timestamp))
                news_count.truncate()
                return last_timestamp
    return 0


def update_actual_on_news():
    db = Database()
    db.db.execute("""
        SELECT id, company_id, UNIX_TIMESTAMP(time)+300 as t FROM news WHERE actual IS NULL AND (UNIX_TIMESTAMP() - UNIX_TIMESTAMP(time)) >= 300
    """)
    news_without_actual = db.db.fetchall()
    if len(news_without_actual) > 0:
        for n in news_without_actual:
            db.db.execute("""
                SELECT current,time FROM prices WHERE company_id = %s AND UNIX_TIMESTAMP(time) >= %s ORDER BY id ASC LIMIT 1
            """, (n["company_id"], int(n["t"])))
            row = db.db.fetchone()
            actual = row["current"]
            db.db.execute("""
                UPDATE news SET actual = %s WHERE id = %s
            """, (actual, n["id"]))
        db.connection.commit()


def get_sentence_info(txt):
    d = dict()
    d['sent_score'] = 0
    d['word_count'] = 0
    word_count = 0
    text = Text(text=txt.encode('utf-8'), hint_language_code='ru')
    for key, c in text.word_counts.items():
        word_count += c
    d['sent_score'] = text.polarity
    d['word_count'] = word_count
    return d


def extract_company(news):
    db = Database()
    parse_names = db.get_all_companies()
    for p in parse_names:
        p['parse_name'] = p['parse_name'].split(', ')
    news_with_one_company = list()
    for d in news:
        d["companies"] = list()
        for company in parse_names:
            for p in company["parse_name"]:
                if p in str(d["text"]):
                    d["companies"].append(company['id'])
                    break
        if len(d["companies"]) == 1:
            d["companies"] = d["companies"][0]
            news_with_one_company.append(d)
    return news_with_one_company


def update_actual_on_news():
    db = Database()
    db.db.execute("""
        SELECT id, company_id, UNIX_TIMESTAMP(time)+300 as t FROM news WHERE actual IS NULL AND (UNIX_TIMESTAMP() - UNIX_TIMESTAMP(time)) >= 300
    """)
    news_without_actual = db.db.fetchall()
    if len(news_without_actual) > 0:
        print("Updating " + str(len(news_without_actual)) + " news")
        for n in news_without_actual:
            db.db.execute("""
                SELECT current,time FROM prices WHERE company_id = %s AND UNIX_TIMESTAMP(time) >= %s ORDER BY id ASC LIMIT 1
            """, (n["company_id"], int(n["t"])))
            row = db.db.fetchone()
            if row is None:
                continue
            actual = row["current"]
            db.db.execute("""
                UPDATE news SET actual = %s WHERE id = %s
            """, (actual, n["id"]))
        db.connection.commit()


if __name__ == '__main__':
    news = get_news()
    current_timestamp = 0
    for n in news:
        current_timestamp = max(current_timestamp, n["timestamp"])
    last_timestamp = update_counter(current_timestamp)
    news_to_update = list()
    if last_timestamp == -1:
        news_to_update = news
    elif last_timestamp != 0:
        for n in news:
            if n["timestamp"] > last_timestamp:
                news_to_update.append(n)
    if len(news_to_update) > 0:
        for n in news_to_update:
            n["info"] = get_sentence_info(n["text"])
        news_to_update = extract_company(news_to_update)
        db = Database()
        print(news_to_update)
        for n in news_to_update:
            db.db.execute("""
                INSERT INTO news(id, company_id, link,body, prediction, actual, time, sent_score, word_count, log_return, trading_volume, overnight_variation, trading_day_variation, closing_price)
                VALUES (NULL, %s, %s,%s,NULL,NULL,FROM_UNIXTIME(%s),%s,%s,NULL,NULL,NULL,NULL,NULL)
            """, (n["companies"], n["url"], n["text"].encode("utf-8"), n["timestamp"], n["info"]["sent_score"],
                  n["info"]["word_count"]))
            db.connection.commit()
        # analysis.calculate_predictions(news_to_update)
    update_actual_on_news()
    print('news updated')
