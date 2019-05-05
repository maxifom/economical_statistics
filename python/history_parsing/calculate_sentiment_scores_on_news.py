"""
    Calculate sentiment score, word count, gets parsed sentence
    and words array from news
"""
from datetime import datetime
from misc.analysis import *
from models import Word


def news_with_one_company():
    positive_words = Word.select().where(Word.is_positive == True)
    negative_words = Word.select().where(Word.is_positive == False)
    df = pd.read_csv("./../../data/news/news_with_one_company.csv")
    df[["sent_score", "word_count", "words", "parsed_sentence"]] = df.apply(sentence_info_pd, axis=1, args=(
        list(positive_words), list(negative_words)))
    df.to_csv("./../../data/news/news_with_one_company_and_sentiment_analysis.csv", index=False)


def news_with_one_or_more_company():
    positive_words = Word.select().where(Word.is_positive == True)
    negative_words = Word.select().where(Word.is_positive == False)
    df = pd.read_csv("./../../data/news/news_with_one_or_more_company.csv")
    df[["sent_score", "word_count", "words", "parsed_sentence"]] = df.apply(sentence_info_pd, axis=1, args=(
        list(positive_words), list(negative_words)))
    df.to_csv("./../../data/news/news_with_one_or_more_company_and_sentiment_analysis.csv", index=False)


if __name__ == '__main__':
    news_with_one_company()
    # news_with_one_or_more_company()
