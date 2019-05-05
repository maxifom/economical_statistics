"""
    Inserts new news and update existing news sentiment info (word count, sentiment score and words list)
"""


import json
from models import News, fn
import pytz
import scrapy
from scrapy.crawler import CrawlerProcess
import logging
from datetime import datetime
from misc.analysis import sentence_info, extract_company

news = list()


def get_news():
    logging.getLogger('scrapy').propagate = False
    logging.getLogger('peewee').propagate = False
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
        n = {}
        body_str = body_str.replace('.', '. ')
        n["body"] = body_str
        n["title"] = title
        n["link"] = response.url
        n["time"] = datetime.utcfromtimestamp(timestamp)
        news.append(n)


def update_sentiment_info_on_existing_news():
    for n in News.select().where(News.word_count.is_null()):
        info = sentence_info(n)
        n.sent_score = info["sent_score"]
        n.word_count = info["word_count"]
        n.words = json.dumps(info["words"])
        n.save()


def insert_new_news():
    last_time = News.select(fn.MAX(News.time).alias("time")).get().time or datetime(1970, 1, 1, 0, 0, 0)
    news = extract_company(get_news())
    news = list(filter(lambda n: n["time"] > last_time, news))
    for n in news:
        dbN = News()
        dbN.title = n["title"]
        dbN.body = n["body"]
        dbN.time = n["time"]
        dbN.link = n["link"]
        dbN.company = n["company"]
        info = sentence_info(dbN)
        dbN.sent_score = info["sent_score"]
        dbN.word_count = info["word_count"]
        dbN.words = json.dumps(info["words"])
        dbN.parsed_sentence = info["sentence"]
        dbN.save()


if __name__ == '__main__':
    insert_new_news()
    update_sentiment_info_on_existing_news()
