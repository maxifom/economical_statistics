import datetime
from datetime import datetime as d

import pytz
import scrapy

from database import Database


class FinamNewsSpider(scrapy.Spider):
    name = "finam_news_spider"

    def start_requests(self):
        urls = list()
        for day in days:
            urls.append('https://www.finam.ru/analysis/conews/rqdate' + day + '/')
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        news = response.xpath('//*[@id="content-block"]/table[2]/tr')
        urls = []
        for n in news:
            urls.append('https://finam.ru' + n.xpath(
                './/a[@class="f-fake-url"]/@href').extract_first())
        for url in urls:
            yield response.follow(url=url, callback=self.parse_news)

    def parse_news(self, response):
        title = response.xpath('//div[@id="news-item"]//h1[1]/text()').extract_first()
        body = response.xpath(
            '//*[contains(@class,"f-newsitem-text")][1]/p/text()').extract()
        body_str = ''
        for text in body:
            body_str += text.replace('\xa0', ' ')
        time = response.xpath(
            '//*[@class="sm lightgrey mb20 mt15"]/text()').extract_first().rstrip('\xa0')
        tz = pytz.timezone("Europe/Moscow")
        timestamp = int(
            tz.localize(d.strptime(time, "%d.%m.%Y %H:%M"), is_dst=0).timestamp())
        n = dict()
        n["text"] = title + '. ' + body_str
        n["url"] = response.url
        n["timestamp"] = timestamp
        news.append(n)


def get_days_to_parse():
    day = d(2017, 1, 1)
    last_day = d.today()
    delta = datetime.timedelta(days=1)
    while day <= last_day:
        if day.weekday() not in (5, 6):
            days.append(to_hex(day))
        day += delta


def hex_of(num):
    h = hex(num).replace('0x', '').upper()
    if len(h) == 1:
        h = '0' + h
    return h


def to_hex(date):
    return hex_of(date.day) + hex_of(date.month) + hex_of(date.year)


days = list()
news = list()


def get_news_history():
    # global news, name
    # get_days_to_parse()
    # logging.getLogger('scrapy').propagate = False
    # price_parsing_process = CrawlerProcess()
    # price_parsing_process.crawl(FinamNewsSpider)
    # price_parsing_process.start()
    # print(news)
    import pickle
    with open('outfile', 'rb') as fp:
        news = pickle.load(fp)
    # print(len(news))
    only_news = list()
    i = 0
    import re
    z = 0
    db = Database()
    db.db.execute("SELECT id,parse_name FROM companies")
    names = db.db.fetchall()
    names_to_search = dict()
    # nums = {n: 0 for n in range(47)}
    for n in names:
        names_to_search[n["id"]] = dict()
        names_to_search[n["id"]]["names"] = n["parse_name"].split(", ")
    for n in news:
        n["companies"] = set()
        i += 1
        found = re.findall(r'\"[A-ZА-Я][a-zA-Zа-яА-Я\s\-.,]*\"', n["text"])
        for f in found:
            for q, w in names_to_search.items():
                for name in w["names"]:
                    if name in f:
                        n["companies"].add(q)  # company id
                        break
        if len(n["companies"]) == 1:
            # print(n["companies"])
            z += 1
            only_news.append(n)
        # if i == 100:
        #     break
    # print(z)
    return only_news


if __name__ == '__main__':
    pass
    # print(get_news_history())

    # for n in news:
    #     if len(n["companies"]) == 1:
    #         nums[n["companies"].pop()] += 1
    # for _, n in nums.items():
    #     if n > 0:
    #         print(n)
