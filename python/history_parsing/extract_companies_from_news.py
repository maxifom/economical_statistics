"""
    Adds companies to news and group them:
    1. News with one company
    2. News with 1+ company
"""

import pandas as pd

from models import Company


def extract_companies():
    companies = Company.select()
    for c in companies:
        c.parse_name = c.parse_name.split(', ')
    df = pd.read_csv('./../../data/news/all_parsed_news.csv')
    df_dict = df.to_dict(orient='rows')
    news_with_one_company = []
    news_with_one_plus_company = []
    for d in df_dict:
        d["companies"] = []
        for company in companies:
            for p in company.parse_name:
                if p in str(d["text"]):
                    d["companies"].append(company.ticker)
                    break
        if len(d["companies"]) == 1:
            d["companies"] = d["companies"][0]
            news_with_one_company.append(d)
        if len(d["companies"]) > 0:
            news_with_one_plus_company.append(d)
    one_company_df = pd.DataFrame(news_with_one_company,
                                  columns=['companies', 'text', 'timestamp', 'url','title']).sort_values(
        by="timestamp").reset_index(drop=True)
    one_company_plus_df = pd.DataFrame(news_with_one_plus_company,
                                       columns=['companies', 'text', 'timestamp', 'url', 'title']).sort_values(
        by="timestamp").reset_index(drop=True)
    one_company_df.to_csv('./../../data/news/news_with_one_company.csv', index=False)
    one_company_plus_df.to_csv('./../../data/news/news_with_one_or_more_company.csv', index=False)


if __name__ == '__main__':
    extract_companies()
