import datetime

import pytz
from multiprocessing.dummy import Pool as ThreadPool
from date_to_hex_converter import DateToHexConverter as Hex
import pandas as pd
import requests
from scrapy import Selector


class FinamNewsParser:

    def __init__(self, start_date=datetime.datetime.now(), end_date=datetime.datetime.now()):
        self.start_date = start_date
        self.end_date = end_date
        self.news = pd.DataFrame(index=["timestamp"], columns=['text', 'url'])

    def get_days_to_parse(self):
        days = list()
        delta = datetime.timedelta(days=1)
        while self.start_date <= self.end_date:
            if self.start_date.weekday() not in (5, 6):  # If not Sat or Sun
                days.append(Hex.to_hex(self.start_date))
            self.start_date += delta
        return days

    def get_links_from_days(self):
        days = self.get_days_to_parse()
        base_url = "https://www.finam.ru/analysis/conews/rqdate"
        urls = list()
        for day in days:
            urls.append(base_url + day + '/')
        return urls

    def parse(self, num_of_threads=8):
        urls = self.get_links_from_days()
        pool = ThreadPool(num_of_threads)
        pool.map(self.process_url, urls)
        pool.close()
        pool.join()

    def process_url(self, url):
        r = requests.get(url=url)
        html = r.text
        sel = Selector(text=html)
        page_news = sel.xpath('//*[@id="content-block"]/table[2]/tr')
        news_urls = list()
        for news in page_news:
            news_urls.append('https://finam.ru' + news.xpath('.//a[@class="f-fake-url"]/@href').extract_first())
        for url in news_urls:
            self.parse_news_url(url)

    def parse_news_url(self, url):
        try:
            r = requests.get(url=url)
            html = r.text
            sel = Selector(text=html)
            title = sel.xpath('//div[@id="news-item"]//h1[1]/text()').extract_first()
            body = sel.xpath(
                '//*[contains(@class,"f-newsitem-text")][1]/p/text()').extract()
            body_str = ''
            for text in body:
                body_str += text.replace('\xa0', ' ')
            time_el = sel.xpath('//*[@class="sm lightgrey mb20 mt15"]/text()').extract_first()
            if time_el is None:
                return
            time = time_el.rstrip('\xa0')
            tz = pytz.timezone("Europe/Moscow")
            timestamp = int(
                tz.localize(datetime.datetime.strptime(time, "%d.%m.%Y %H:%M"), is_dst=0).timestamp())
            n = dict()
            n["timestamp"] = timestamp
            n["text"] = title + '. ' + body_str
            n["url"] = url
            p = pd.DataFrame(n, index=[timestamp])
            self.news = pd.concat([self.news, p], sort=True)
            print(self.news.shape)
        except:
            print('error occured')
            return

    def save_news(self, file):
        self.news.to_csv(file)


if __name__ == '__main__':
    now = datetime.datetime.now()
    parser = FinamNewsParser(datetime.datetime(2017, 1, 1, 0, 0, 0))
    parser.parse(8)
    parser.save_news('./csv/all_parsed_news.csv')
    print(datetime.datetime.now() - now)
