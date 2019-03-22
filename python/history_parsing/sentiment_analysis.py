import numpy
from polyglot.text import Text
import pandas as pd

from analysis import sentence_info


def calculate_sent_score(series):
    for s in series:
        if str(s) != 'nan':
            return Text(text=s.encode('utf-8'), hint_language_code='ru').polarity
        else:
            return numpy.NaN


def add_sentiment_scores():
    df = pd.read_csv('./../../data/all_parsed_news.csv')
    df_dict = df.to_dict(orient='rows')
    index = 0
    print("Len", len(df_dict))
    for d in df_dict:
        if index % 1000 == 0:
            print(index)
        index += 1
        if 'nan' in str(d["text"]):
            d['sent_score'] = 0
            d['word_count'] = 0
            continue
        info = sentence_info(d["text"])
        # word_count = 0
        # text = Text(text=d['text'].encode('utf-8'), hint_language_code='ru')
        # for key, c in text.word_counts.items():
        #     word_count += c
        d['sent_score'] = info["sent_score"]
        d['word_count'] = info["word_count"]
    df = pd.DataFrame.from_dict(df_dict)
    df.to_csv('./../../data/all_parsed_news_with_sentiment_scores.csv')

def sentiment_companies():
    df = pd.read_csv('./../../data/news_with_one_company.csv')
    df_dict = df.to_dict(orient='rows')
    index = 0
    print("Len", len(df_dict))
    for d in df_dict:
        if index % 1000 == 0:
            print(index)
        index += 1
        if 'nan' in str(d["text"]):
            d['sent_score'] = 0
            d['word_count'] = 0
            continue
        info = sentence_info(d["text"])
        # word_count = 0
        # text = Text(text=d['text'].encode('utf-8'), hint_language_code='ru')
        # for key, c in text.word_counts.items():
        #     word_count += c
        d['sent_score'] = info["sent_score"]
        d['word_count'] = info["word_count"]
    df = pd.DataFrame.from_dict(df_dict)
    df.to_csv('./../../data/news_with_one_company_sent_scores.csv')


if __name__ == '__main__':
    add_sentiment_scores()
