import logging
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


if __name__ == '__main__':
    logging.getLogger('scrapy').propagate = False
    price_parsing_process = CrawlerProcess()
    price_parsing_process.crawl(InvestingComSpider)
    price_parsing_process.start()
    print("Parsing successful")
