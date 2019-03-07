import logging
from datetime import datetime

import MySQLdb.cursors
import scrapy
from scrapy.crawler import CrawlerProcess


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
        db.insert_companies(companies)


class Formatter:
    @staticmethod
    def format_volume(volume):
        if 'K' in volume:
            volume = float(volume.replace('.', '').replace(',', '.').replace('K', '')) * 1e3
        elif 'M' in volume:
            volume = float(volume.replace('.', '').replace(',', '.').replace('M', '')) * 1e6
        elif 'B' in volume:
            volume = float(volume.replace('.', '').replace(',', '.').replace('B', '')) * 1e9
        return int(volume)

    @staticmethod
    def format_price(price):
        return float(price.replace('.', '').replace(',', '.'))


class Database:
    def __init__(self, connection):
        self.connection = connection
        self.db = self.connection.cursor()
        self.db.execute('''
            SET NAMES utf8;
            SET CHARACTER SET utf8;
            SET character_set_connection=utf8;
        ''')
        with open('schema.sql', 'r') as schema:
            self.db.execute(schema.read().replace('\n', ''))

    def insert_companies(self, givenCompanies):
        self.db.execute("""
            SELECT COUNT(1) as count FROM companies
        """)
        count = self.db.fetchone()["count"]
        if count == 0:
            for name, company in givenCompanies.items():
                self.db.execute("""
                    INSERT INTO companies (name,full_name)
                    VALUES (%s,%s)
                """, (name.encode('utf-8'), company["full_name"].encode('utf-8')))

            self.connection.commit()
        self.db.execute("""
            SELECT * from companies
        """)
        companies = self.db.fetchall()
        for company in companies:
            givenCompanies[company["name"]]["id"] = company["id"]
        for name, company in givenCompanies.items():
            self.db.execute("""
                SELECT company_id, volume,time FROM prices 
                WHERE company_id = %s ORDER BY id DESC LIMIT 1
            """, (company["id"],))
            last = self.db.fetchone()
            company_time = datetime.utcfromtimestamp(company["time"])
            if not last or company_time != last["time"]:
                if not last:
                    last_volume = company["volume"]
                else:
                    last_volume = last["volume"]
                self.db.execute("""
                    INSERT INTO prices(company_id, current,high,low,volume,volume_previous,time)
                    VALUES (%s,%s,%s,%s,%s,%s, FROM_UNIXTIME(%s))
                """, (company["id"],
                      company["current_price"],
                      company["high_price"],
                      company["low_price"],
                      company["volume"],
                      company["volume"] - last_volume,
                      company["time"],
                      ))
        self.connection.commit()
        return

    def __del__(self):
        self.connection.close()


if __name__ == '__main__':
    conn = MySQLdb.connect('localhost', 'user', 'user', 'economics', cursorclass=MySQLdb.cursors.DictCursor)
    db = Database(conn)
    logging.getLogger('scrapy').propagate = False
    process = CrawlerProcess()
    process.crawl(InvestingComSpider)
    process.start()
