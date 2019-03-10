import logging
from datetime import datetime

import pytz
import scrapy
from scrapy.crawler import CrawlerProcess

from database import Database
from format import Formatter


class InvestingComSpider(scrapy.Spider):
    name = "investing_com_spider"

    def start_requests(self):
        urls = ["https://ru.investing.com/indices/mcx-components"]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        companies = dict()
        companies_info = response.css('table#cr1 > tbody').xpath('./tr[contains(@id,"pair")]')
        for company in companies_info:
            name_el = company.xpath('./td[2]/a')
            name = name_el.xpath('./text()').extract_first()
            full_name = name_el.xpath('./@title').extract_first()
            companies[name] = dict()
            current_price = company.xpath('./td[contains(@class,"last")]/text()').extract_first()
            current_price = Formatter.format_price(current_price)
            high_price = company.xpath('./td[contains(@class,"high")]/text()').extract_first()
            high_price = Formatter.format_price(high_price)
            low_price = company.xpath('./td[contains(@class,"low")]/text()').extract_first()
            low_price = Formatter.format_price(low_price)
            volume = company.xpath('./td[contains(@class,"turnover")]/text()').extract_first()
            volume = Formatter.format_volume(volume)
            update_time = int(company.xpath('./td[contains(@class,"time")]/@data-value').extract_first())
            companies[name]["current_price"] = current_price
            companies[name]["high_price"] = high_price
            companies[name]["low_price"] = low_price
            companies[name]["volume"] = volume
            companies[name]["full_name"] = full_name
            companies[name]["time"] = update_time
        db = Database()
        db.insert_companies(companies)


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
        body = response.xpath('//*[contains(@class,"f-newsitem-text")][1]/p/text()').extract()
        body_str = ''
        for text in body:
            body_str += text.replace('\xa0', ' ')
        time = response.xpath('//*[@class="f-newsitem"][1]/div[2]/text()').extract_first().rstrip('\xa0')
        tz = pytz.timezone("Europe/Moscow")
        timestamp = int(tz.localize(datetime.strptime(time, "%d.%m.%Y %H:%M"), is_dst=0).timestamp())
        n = dict()
        n["text"] = title + '. ' + body_str
        n["url"] = response.url
        n["timestamp"] = timestamp
        news.append(n)


def parse_companies_and_insert_prices():
    logging.getLogger('scrapy').propagate = False
    price_parsing_process = CrawlerProcess()
    price_parsing_process.crawl(InvestingComSpider)
    price_parsing_process.start(stop_after_crawl=False)


news = list()


def get_news():
    logging.getLogger('scrapy').propagate = False
    spider = FinamNewsSpider()
    news_parsing_process = CrawlerProcess()
    news_parsing_process.crawl(spider)
    news_parsing_process.start()
    return news


def parse_companies_and_get_news():
    logging.getLogger('scrapy').propagate = False
    parsing_process = CrawlerProcess()
    news_spider = FinamNewsSpider()
    parsing_process.crawl(InvestingComSpider)
    parsing_process.crawl(news_spider)
    parsing_process.start()
    return news
