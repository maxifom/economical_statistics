import json

import pandas as pd

from models import News


def convert_to_dict(x):
    return json.loads(x.replace("'", '"'))


def save_word_cloud_to_file():
    df = pd.read_csv("./../../data/news/news_with_one_company_and_sentiment_analysis.csv")
    df.words = df.words.apply(convert_to_dict)
    df_words = df.words.to_dict()
    all_words = {}
    positive_words = {}
    negative_words = {}
    for _, words in df_words.items():
        for w in words:
            if w["score"] > 0:
                positive_words[w["word"]] = positive_words.get(w["word"], 0) + w["count"] * w["score"]
            elif w["score"] < 0:
                negative_words[w["word"]] = negative_words.get(w["word"], 0) - w["count"] * w["score"]
            all_words[w["word"]] = all_words.get(w["word"], 0) + w["count"] * w["score"]
    news = News.select(News.words)
    for n in news:
        n.words = json.loads(n.words)
        for w in n.words:
            if w["score"] > 0:
                positive_words[w["word"]] = positive_words.get(w["word"], 0) + w["count"] * w["score"]
            elif w["score"] < 0:
                negative_words[w["word"]] = negative_words.get(w["word"], 0) - w["count"] * w["score"]
            all_words[w["word"]] = all_words.get(w["word"], 0) + w["count"] * w["score"]
    with open("./../../data/word_cloud/word_cloud.json", "w") as file:
        json.dump({"all_words": all_words, "positive_words": positive_words, "negative_words": negative_words}, file)


if __name__ == '__main__':
    save_word_cloud_to_file()
