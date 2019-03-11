import sys

import spiders

if __name__ == '__main__':
    spiders.parse_companies_and_insert_prices()
    print("Prices updated")
    sys.exit()
