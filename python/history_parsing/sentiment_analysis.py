import numpy
from polyglot.text import Text
import pandas as pd


def calculate_sent_score(series):
    for s in series:
        if str(s) != 'nan':
            return Text(text=s.encode('utf-8'), hint_language_code='ru').polarity
        else:
            return numpy.NaN


if __name__ == '__main__':
    df = pd.read_csv('./csv/all_parsed_news.csv')
    df_dict = df.to_dict(orient='rows')
    for d in df_dict:
        if 'nan' in str(d["text"]):
            d['sent_score'] = 0
            d['word_count'] = 0
            continue
        word_count = 0
        text = Text(text=d['text'].encode('utf-8'), hint_language_code='ru')
        for key, c in text.word_counts.items():
            word_count += c
        d['sent_score'] = text.polarity
        d['word_count'] = word_count
    df = pd.DataFrame.from_dict(df_dict)
    df.to_csv('./csv/all_parsed_news_with_sentiment_scores.csv')
