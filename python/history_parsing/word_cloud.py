import os

import math
import pandas as pd
from misc.database import Database
from misc.analysis import sentence_info
import pickle
from datetime import datetime, timedelta


def word_cloud_history():
    t = datetime.now()
    db = Database()
    db.db.execute("""
                SELECT word from words WHERE is_positive=1
            """)
    positive = db.db.fetchall()
    db.db.execute("""
                    SELECT word from words WHERE is_positive=0
                """)
    negative = db.db.fetchall()
    positive = sorted(positive, key=lambda x: len(x["word"].split(' ')), reverse=True)
    negative = sorted(negative, key=lambda x: len(x["word"].split(' ')), reverse=True)
    df = pd.read_csv("./../../data/news_with_one_company_sent_scores.csv")
    df.drop(columns=["timestamp", "companies", "sent_score", "url", "word_count", "Unnamed: 0", "Unnamed: 0.1"],
            inplace=True)
    df.dropna(inplace=True)
    df_dict = df.to_dict(orient='rows')
    all_words = []
    l = len(df_dict)
    i = 0
    for d in df_dict:
        all_words.append(sentence_info(d["text"], positive, negative)["words"])
        if i % 1000 == 0:
            print(datetime.now() - t)
            print(i, l)
        i += 1
    with open("./../../data/all_words.pickle", "wb") as f:
        pickle.dump(all_words, f)


def word_cloud_rt():
    with open("./../../data/all_words.pickle", "rb") as f:
        all_words = pickle.load(f)
    files = os.listdir("./../../data/")
    import re
    news_files = []
    regex = r"^news_[0-9]*_words$"
    for f in files:
        if re.match(regex, f):
            news_files.append(f)
    print(len(all_words))
    for n in news_files:
        with open(f"./../../data/{n}", "rb") as f:
            all_words.append(pickle.load(f))
    print(len(all_words))
    with open("./../../data/all_words2.pickle", "wb") as f:
        pickle.dump(all_words, f)


def save_all_words_to_file():
    with open("./../../data/all_words2.pickle", "rb") as f:
        all_words = pickle.load(f)
    words = dict()
    positive_words = dict()
    negative_words = dict()
    # print(all_words[4])
    for word in all_words:
        for w in word["words"]:
            words[w["word"]] = words.get(w["word"], 0) + w["score"] * w["count"]
            if w["score"] > 0:
                positive_words[w["word"]] = positive_words.get(w["word"], 0) + w["score"] * w["count"]
            elif w["score"] < 0:
                negative_words[w["word"]] = negative_words.get(w["word"], 0) - w["score"] * w["count"]
    # print(len(words), len(positive_words), len(negative_words))
    # print(words)
    # print(positive_words)
    # print(negative_words)
    with open("./../../data/word_cloud_data", "wb") as p:
        pickle.dump((words, positive_words, negative_words), p)


if __name__ == '__main__':
    # word_cloud_history()
    # word_cloud_rt()
    save_all_words_to_file()
    with open("./../../data/word_cloud_data", "rb") as p:
        print(pickle.load(p)[0])
