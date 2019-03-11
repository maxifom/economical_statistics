import logging

import scrapy
from scrapy.crawler import CrawlerProcess

from database import Database


class InvestingComSpider(scrapy.Spider):
    name = "investing_com_spider"

    def start_requests(self):
        urls = ["https://ru.investing.com/indices/mcx-components"]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        companies = list()
        companies_info = response.css('table#cr1 > tbody').xpath('./tr[contains(@id,"pair")]')
        for company in companies_info:
            c = dict()
            url = "https://ru.investing.com" + company.xpath(
                './td[@class="bold left noWrap elp plusIconTd"]/a[1]/@href').extract_first()
            c["url"] = url
            name_el = company.xpath('./td[2]/a')
            name = name_el.xpath('./text()').extract_first()
            c["name"] = name
            companies.append(c)
        db = Database()
        for c in companies:
            db.db.execute("""
                UPDATE companies SET url = %s WHERE name = %s
            """, (c["url"], c["name"].encode('utf-8')))
            db.connection.commit()


if __name__ == '__main__':
    logging.getLogger('scrapy').propagate = False
    price_parsing_process = CrawlerProcess()
    price_parsing_process.crawl(InvestingComSpider)
    price_parsing_process.start()
