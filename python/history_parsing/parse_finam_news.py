"""
    Parse company news from Finam.ru
"""

import datetime

import pytz
from multiprocessing.dummy import Pool as ThreadPool
import pandas as pd
from scrapy import Selector

import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

s = requests.Session()
retries = Retry(total=5, backoff_factor=0.1)
s.mount("https://", HTTPAdapter(max_retries=retries))


class FinamNewsParser:

    def __init__(self, start_date=datetime.datetime.utcnow(), end_date=datetime.datetime.utcnow()):
        self.start_date = start_date
        self.end_date = end_date
        self.news = pd.DataFrame(index=["timestamp"], columns=['text', 'url', 'title'])

    def get_days_to_parse(self):
        days = list()
        delta = datetime.timedelta(days=1)
        while self.start_date <= self.end_date:
            if self.start_date.weekday() not in (5, 6):  # If not Sat or Sun
                days.append(self.start_date.strftime("%Y-%m-%d"))
            self.start_date += delta
        return days

    def get_links_from_days(self):
        days = self.get_days_to_parse()
        base_url = "https://www.finam.ru/analysis/conews/"
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
        r = s.get(url=url)
        if r.status_code != 200:
            print(r.status_code)
        if r.url != url:
            return
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
            r = s.get(url=url)
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
            n["text"] = body_str
            n["title"] = title
            n["url"] = url
            p = pd.DataFrame(n, index=[timestamp])
            self.news = pd.concat([self.news, p], sort=True)
            print(self.news.shape[0])
        except Exception as e:
            print(e, 'error occured')
            return

    def save_news_with_postprocess(self, file):
        self.news.dropna(inplace=True)
        self.news.drop_duplicates(subset=["text", "timestamp"], inplace=True)
        self.news.sort_values(by=["timestamp"], inplace=True)
        self.news.reset_index(inplace=True)
        self.news["timestamp"] = pd.to_datetime(self.news["timestamp"], unit="s")
        self.news.to_csv(file, index=False)


if __name__ == '__main__':
    now = datetime.datetime.utcnow()
    parser = FinamNewsParser(datetime.datetime(2000, 1, 1, 0, 0, 0))
    parser.parse(16)
    parser.save_news_with_postprocess('./../../data/news/all_parsed_news.csv')
    print(datetime.datetime.utcnow() - now)
