import os
from datetime import datetime

from companies_extractor import extract_companies
from linreg_coef_final import calculate_linreg_coef_and_pvalues
from linreg_params_final import calculate_params
from sentiment_analysis import sentiment_companies
from reparse_news_from_db import parse_news
from true_percent import calculate_percent_true

def reparse():
    try:
        time = datetime.now()
        print("Extracting companies")
        extract_companies()
        print(datetime.now() - time)
        print("adding sent scores")
        sentiment_companies()
        print(datetime.now() - time)
        print("Calculating linreg params")
        calculate_params()
        print(datetime.now() - time)
        print("Calculating coefs and pvalues")
        calculate_linreg_coef_and_pvalues()
        print(datetime.now() - time)
        print("Reparsing db news")
        parse_news()
        print(datetime.now() - time)
        print("Calculate percent true")
        calculate_percent_true()
        print(datetime.now() - time)
    except Exception:
        print("e")
    finally:
        with open('./../is_parsing', 'w') as file:
            file.write(str(0))


def try_reparse():
    if os.path.exists('./../need_parsing'):
        with open('./../need_parsing', 'r') as file:
            if int(file.read()) == 1:
                with open('./../need_parsing', 'w') as w:
                    w.write(str(0))
                reparse()


if __name__ == '__main__':
    try_reparse()
