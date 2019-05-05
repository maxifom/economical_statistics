"""
    Adds average sentiment score and word count to price info
    (for further linear regression calculation)
"""

from datetime import datetime

import pandas as pd

from models import Company


def mean_sent_score_and_word_count(x, news, ticker):
    time = datetime.strptime(x.date, "%Y-%m-%d")
    start_time = time.replace(hour=0, minute=0, second=0, microsecond=0)
    end_time = time.replace(hour=23, minute=59, second=59, microsecond=999999)
    daily_news = news[(news["company"] == ticker) & (start_time.timestamp() <= news["timestamp"]) & (
            news["timestamp"] <= end_time.timestamp())]
    sent_score = daily_news.sent_score.mean()
    word_count = daily_news.word_count.mean()
    return pd.Series([sent_score, word_count])


if __name__ == '__main__':
    news = pd.read_csv("./../../data/news/news_with_one_company_and_sentiment_analysis.csv")
    news.rename(columns={"companies": "company"}, inplace=True)
    companies = Company.select()
    for c in companies:
        df = pd.read_csv(f"./../../data/prices/{c.ticker}.csv")
        df[["sent_score", "word_count"]] = df.apply(mean_sent_score_and_word_count, axis=1, args=(news, c.ticker))
        df.sent_score.fillna(0, inplace=True)
        df.word_count.fillna(0, inplace=True)
        df.to_csv(f"./../../data/all_params/{c.ticker}.csv", index=False)
