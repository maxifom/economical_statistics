"""
    Updates prices from finam and inserts into database
"""

from datetime import datetime
import requests
from scrapy import Selector
from misc.format import Formatter
from models import Price


def parse_prices():
    url = "https://ru.investing.com/indices/mcx-components"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/73.0.3683.86 YaBrowser/19.4.0.2397 Yowser/2.5 Safari/537.36 "
    }
    r = requests.get(url=url, headers=headers)
    sel = Selector(text=r.text)
    companies_info = sel.css('table#cr1 > tbody').xpath('./tr[contains(@id,"pair")]')
    for company in companies_info:
        current_price = company.xpath('./td[contains(@class,"last")]/text()').extract_first()
        current_price = Formatter.format_price(current_price)
        high_price = company.xpath('./td[contains(@class,"high")]/text()').extract_first()
        high_price = Formatter.format_price(high_price)
        low_price = company.xpath('./td[contains(@class,"low")]/text()').extract_first()
        low_price = Formatter.format_price(low_price)
        volume = company.xpath('./td[contains(@class,"turnover")]/text()').extract_first()
        volume = Formatter.format_volume(volume)
        update_time = int(company.xpath('./td[contains(@class,"time")]/@data-value').extract_first())
        p = Price()
        p.current = current_price
        p.high = high_price
        p.low = low_price
        p.volume = volume
        p.time = datetime.fromtimestamp(update_time)
        p.save()


if __name__ == '__main__':
    parse_prices()
    print("Parsing successful")
